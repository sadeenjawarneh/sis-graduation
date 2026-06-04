from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import UserRole
from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer, ChangePasswordSerializer

User = get_user_model()


def _token_response(user, request, status_code=200):
    refresh = RefreshToken.for_user(user)
    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user':    UserSerializer(user, context={'request': request}).data,
    }, status=status_code)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    s = RegisterSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    user = s.save()
    return _token_response(user, request, 201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = (request.data.get('email') or '').strip()
    password = request.data.get('password') or ''
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password.'}, status=401)
    if not user_obj.is_active or not user_obj.check_password(password):
        return Response({'error': 'Invalid email or password.'}, status=401)
    return _token_response(user_obj, request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        RefreshToken(request.data.get('refresh')).blacklist()
    except (TokenError, Exception):
        pass
    return Response({'detail': 'Logged out.'}, status=200)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user, context={'request': request}).data)
    s = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(UserSerializer(request.user, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    s = ChangePasswordSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    if not request.user.check_password(s.validated_data['old_password']):
        return Response({'error': 'Old password incorrect.'}, status=400)
    request.user.set_password(s.validated_data['new_password'])
    request.user.save()
    return Response({'detail': 'Password changed.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list(request):
    """GET /api/v1/auth/students/ — list all students (admin only)"""
    if request.user.role != UserRole.ADMIN:
        return Response({'error': 'Admin only.'}, status=403)
    students = User.objects.filter(role=UserRole.STUDENT, is_active=True).order_by('display_name')
    return Response(UserSerializer(students, many=True, context={'request': request}).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def supervisor_list(request):
    if request.method == 'POST':
        if request.user.role != UserRole.ADMIN:
            return Response({'error': 'Admin only.'}, status=403)
        email        = (request.data.get('email') or '').strip().lower()
        display_name = (request.data.get('first_name', '') + ' ' + request.data.get('last_name', '')).strip() \
                       or request.data.get('display_name', email)
        department   = request.data.get('department', '')
        if not email:
            return Response({'error': 'Email is required.'}, status=400)
        if User.objects.filter(email__iexact=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=400)
        sup = User.objects.create_user(
            email=email, password='Supervisor0*',
            display_name=display_name, role=UserRole.SUPERVISOR,
            department=department, is_active=True,
        )
        return Response({'success': True, 'message': f'Supervisor {display_name} created.', 'id': sup.id}, status=201)

    sups = User.objects.filter(role=UserRole.SUPERVISOR, is_active=True).order_by('display_name')
    return Response(UserSerializer(sups, many=True, context={'request': request}).data)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def supervisor_detail(request, pk):
    if request.user.role != UserRole.ADMIN:
        return Response({'error': 'Admin only.'}, status=403)
    sup = get_object_or_404(User, pk=pk)

    if request.method == 'DELETE':
        from apps.teams.models import Team
        if Team.objects.filter(assigned_supervisor=sup).exists():
            return Response({'success': False, 'message': 'Cannot delete: supervisor has assigned teams.'}, status=400)
        sup.delete()
        return Response({'success': True, 'message': 'Supervisor deleted.'})

    if request.method == 'PUT':
        first = (request.data.get('first_name') or '').strip()
        last  = (request.data.get('last_name')  or '').strip()
        new_name = (first + ' ' + last).strip()
        if new_name:
            sup.display_name = new_name
        if 'department' in request.data:
            sup.department = request.data['department']
        if 'email' in request.data and request.data['email']:
            email = request.data['email'].strip().lower()
            if not User.objects.filter(email__iexact=email).exclude(pk=sup.pk).exists():
                sup.email = email
        sup.save()
        return Response({'success': True, 'message': 'Supervisor updated.'})
