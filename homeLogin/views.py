from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import UserSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import update_session_auth_hash

#Página de login
@api_view(['POST'])
@csrf_exempt
def login(request):

    #Comprueba que exista un usuario en la base de datos
    user = get_object_or_404(User, username=request.data['username'])
    
    #confirma que exista el password previamente creado en register_user
    if user.check_password(request.data['password']):
        return Response({'errors': 'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)
    token = Token.objects.create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
 
 #Página de registro de usuario   
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def register_user(request):
    #Serializar los datos proporcionados
    serializer = UserSerializer(data=request.data)
    # Obtener los datos del cuerpo de la solicitud
    if serializer.is_valid():
        serializer.save()

        user = User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Registrar si estás logeado con un token
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    
    if request.method == 'GET':
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get("email")
    
    if not email:
        return Response({"error": "Correo electrónico es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si hay múltiples usuarios con el mismo correo
    users = User.objects.filter(email=email)
    
    if users.count() > 1:
        return Response({"error": "Hay múltiples usuarios con este correo"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)  # Encuentra al usuario por correo
    except User.DoesNotExist:
        return Response({"error": "No se encontró el mail"}, status=status.HTTP_404_NOT_FOUND)
    
    token = account_activation_token.make_token(user)  # Genera el token
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # ID en base64
    
    # Renderiza el mensaje del correo
    subject = "Restablecimiento de Contraseña"
    message = (
        f"Hola {user.username},\n\n"
        "Para restablecer tu contraseña, necesitarás los siguientes datos:\n"
        f"UID: {uid}\n"
        f"Token: {token}\n\n"
        "Usa estos datos para restablecer tu contraseña.\n\n"
        "Si no solicitaste este restablecimiento, puedes ignorar este mensaje.\n"
    )
    send_mail(
        "Restablecimiento de Contraseña",
        message,  # Mensaje con UID y Token sin URL
        "arielstarsoft@gmail.com",
        [user.email],  # El destinatario
    )
    
    return Response({"message": "Se ha enviado un correo para restablecer la contraseña"}, status=status.HTTP_200_OK)

#Separa el código para poder resetear la contraseña, volver a solicitar una nueva contraseña

@api_view(['POST'])
def password_reset_confirm(request):
    uidb64 = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Token inválido o usuario no encontrado"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verifica el token
    if account_activation_token.check_token(user, token):
        user.set_password(new_password)  # Establece la nueva contraseña
        user.save()
        
        # Opcional: Mantener la sesión autenticada después de restablecer la contraseña
        update_session_auth_hash(request, user)
        
        return Response({"message": "Contraseña restablecida con éxito"}, status=status.HTTP_200_OK)
    
    return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)
