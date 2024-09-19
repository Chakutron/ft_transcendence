# /pong/game/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .matchmaking import match_maker
from .tournament import tournament_match_maker
from .models import Player
import asyncio

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.game = None
        print("User connected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'authenticate':
            await self.authenticate(data['token'])
        elif data['type'] == 'authenticate2':
            await self.authenticate2(data['token_1'], data['token_2'])
        elif data['type'] == 'authenticate3':
            await self.authenticate3(data['token'])
        elif data['type'] == 'key_press':
            if self.game:
                await self.game.handle_key_press(self, data['key'])
        elif data['type'] == 'start_tournament':
            print(f"Start TOURNAMENT received by {self.user}")
            # Run the tournament in the background
            asyncio.create_task(tournament_match_maker.start_tournament())

    async def authenticate(self, token):
        user = await self.get_user_from_token(token)
        if user:
            self.user = user
            await self.send(text_data=json.dumps({'type': 'authenticated'}))
            print(f"User {self.user} authenticated")
            await self.join_waiting_room()
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            print("Authentication failed")

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            user = User.objects.filter(auth_token=token).first()
            return user
        except User.DoesNotExist:
            return None

    async def join_waiting_room(self):
        await self.send(text_data=json.dumps({'type': 'waiting_room'}))
        await match_maker.add_player(self)

    async def authenticate2(self, token, token2):
        user = await self.get_user_from_token(token)
        if user:
            self.user = user
            await self.send(text_data=json.dumps({'type': 'authenticated'}))
            print(f"User {self.user} authenticated")
            user2 = await self.get_user_from_token2(token2)
            if user2:
                self.user2 = user2
                await self.send(text_data=json.dumps({'type': 'authenticated'}))
                print(f"User {self.user2} authenticated")
                await match_maker.create_game(self, None, True)
            else:
                await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
                print("Authentication failed")
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            print("Authentication failed")

    @database_sync_to_async
    def get_user_from_token2(self, token):
        try:
            user2 = User.objects.filter(auth_token=token).first()
            return user2
        except User.DoesNotExist:
            return None

    async def authenticate3(self, token):
        user = await self.get_user_from_token(token)
        if user:
            self.user = user
            await self.send(text_data=json.dumps({'type': 'authenticated'}))
            print(f"User {self.user.username} authenticated for tournament")
            await self.join_tournament_waiting_room()
        else:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            print("Tournament authentication failed")

    async def join_tournament_waiting_room(self):
        await tournament_match_maker.add_player(self)

    async def disconnect(self, close_code):
        if self.game:
            await self.game.end_game(disconnected_player=self)
        await match_maker.remove_player(self)
        await tournament_match_maker.remove_player(self)
        print(f"User {self.user.username if hasattr(self, 'user') else 'Unknown'} disconnected")

    async def set_game(self, game):
        print(f"({self.user}) Game set to: {game}")
        self.game = game

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_group_name = self.scope['url_route']['kwargs']['room_name']
				
		await self.accept()
			
		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)

		self.username = self.scope['user'].username
		

	async def disconnect(self, close_code):
		# Retirer l'utilisateur du groupe (room)
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)
		# Retirer l'utilisateur de son groupe personnel
		await self.channel_layer.group_discard(
			f"user_{self.username}",
			self.channel_name
		)
		# Envoyer un message indiquant que l'utilisateur a quitté la room
		await self.chat_message(
			'chat_message',
			self.user.username if hasattr(self, "user") else "Unknown",
			f'{self.user.username if hasattr(self, "user") else "Unknown"} a quitté le chat',
			self.room_group_name
		)
	
	async def receive(self, text_data):
		try:
			# Convertir les données JSON reçues en dictionnaire Python
			data = json.loads(text_data)
			message_type = data.get('type')
			username = data.get('username')
			message = data.get('message', None)
			target_user = data.get('target_user', None)
			# Gestion des différents types de messages
			if message_type == 'authenticate':
				await self.authenticate(data.get('token'), username)
				return
			elif message_type == 'chat_message':
				await self.chat_message('chat_message', username, message, self.room_group_name)
			elif message_type == 'block_user':
				await self.handle_block_user(data)
			elif message_type == 'invite':
				await self.handle_invite_user(data)
			elif message_type == 'invite_response':
				await self.handle_invite_response(data)
			else:
				await self.chat_message('error', 'server', f"Unhandled message type: {message_type}", self.room_group_name)
		except json.JSONDecodeError as e:
			await self.chat_message('error', 'server', 'Invalid JSON format', self.room_group_name)
		except Exception as e:
			await self.chat_message('error', 'server', 'Internal server error', self.room_group_name)

	async def chat_message(self, message_type, username, message, room):
		# Utilisation de channel_layer pour envoyer le message à tout le groupe (room)
		await self.channel_layer.group_send(
			room,
			{
				'type': 'send_group_message',  # Nom de la méthode qui va gérer ce message
				'username': username,
				'message': message,
				'room': room
			}
		)

	async def send_group_message(self, event):
		message = event['message']
		username = event.get('username', 'Anonyme')
		room = event.get('room', 'unknown')

		# Envoi du message à chaque utilisateur dans la room via WebSocket
		await self.send(text_data=json.dumps({
			'type': 'chat_message',  # Le type de message qui sera renvoyé au client
			'username': username,
			'message': message,
			'room': room
		}))

	async def handle_block_user(self, data):
		username = data['username']
		target_user = data['target_user']
		if target_user == username:
			logger.warning(f"{username} a tenté de se bloquer lui-même.")
			await self.send(text_data=json.dumps({'type': 'error', 'message': 'You cannot block yourself'}))
			return
		# Utilisation correcte de l' f-string pour inclure la valeur de target_user
		await self.send(text_data=json.dumps({
			'type': 'block_user',
			'message': f'Vous avez bloqué les messages de {target_user}'
		}))

	async def handle_invite_user(self, data):
		# Récupération des informations de l'invitation
		inviter = data.get('username')
		target_user = data.get('target_user')
		room = data.get('room')
		# Validation des paramètres
		if not inviter:
			await self.chat_message('error', 'server', 'Invitant manquant', self.room_group_name)
			return
		if not target_user:
			await self.chat_message('error', 'server', 'Utilisateur cible manquant', self.room_group_name)
			return
		if not room:
			await self.chat_message('error', 'server', 'Room manquante', self.room_group_name)
			return
		await self.chat_message('chat_message', 'server', f'{inviter} a invité {target_user} à rejoindre une partie {room}', room)
		# Envoi de l'invitation
		await self.channel_layer.group_send(
			room,
			{
				'type': 'invite',
				'inviter': inviter,
				'target_user': target_user,
				'room': room,
				'message': f'{inviter} vous a invité à rejoindre la room {room}.'
			}
		)

	async def handle_invite_response(self, data):
		inviter = data.get('inviter')
		username = data.get('username')  # L'utilisateur invité qui répond
		response = data.get('response')
		room = data.get('room')

		await self.chat_message('chat_message', 'server', f'{username} a répondu {response} à l\'invitation.', room)

		if response.lower() == 'yes':
			try:
				await self.channel_layer.group_send(
					room,
					{
						'type': 'invite_response',
						'inviter': inviter,
						'username': username,
						'response': response,
						'room': room,
						'message': f'{username} a accepté l\'invitation.'
					}
				)
				 # Informer à la fois l'invité et l'invitant que le jeu va commencer
				await self.channel_layer.group_send(
					room,
					{
						'type': 'start_quick_match',
						'inviter': inviter,
						'username': username,
						'message': 'La partie va démarrer pour vous deux.',
					}
				)
			except Exception as e:
				await self.chat_message('error', 'server', f'Internal server error: {str(e)}', room)
			
	# Méthode appelée pour envoyer l'invitation à l'utilisateur invité (target_user)
	async def invite(self, event):
		inviter = event['inviter']
		message = event['message']
		room = event['room']
		target_user = event['target_user']
		# Envoyer le message d'invitation via WebSocket
		await self.send(text_data=json.dumps({
			'type': 'invite',
			'inviter': inviter,
			'target_user': target_user,
			'message': message,
			'room': room
		}))

	async def handle_invite_response(self, data):
		inviter = data.get('inviter')
		username = data.get('username')  # L'utilisateur invité qui répond
		response = data.get('response')
		room = data.get('room')

		await self.chat_message('chat_message', 'server', f'{username} a répondu {response} à l\'invitation.', room)

		# Envoi de la réponse directement à l'invitant dans la room
		await self.channel_layer.group_send(
			room,
			{
				'type': 'invite_response',  # Type de message 'invite_response'
				'inviter': inviter,
				'username': username,
				'room': room,
				'message': f'{username} a répondu {response} à l\'invitation.',
				'response': response  # Ajout de la réponse 'yes' ou 'no'
			}
		)

	async def invite_response(self, event):
		message = event['message']
		response = event.get('response')
		inviter = event.get('inviter')  # Récupérer l'inviteur		
		# Envoyer la réponse à l'invitation via WebSocket à l'invitant
		await self.send(text_data=json.dumps({
			'type': 'invite_response',
			'message': message,
			'response': response,
			'inviter': inviter
		}))


	async def authenticate(self, token, username):
		if not token:
			await self.chat_message('error', 'server', 'Token is missing', self.room_group_name)
			return
		try:
			user = await self.get_user_from_token(token)
			if user:
				self.user = user
				await self.chat_message('authenticated', username, 'Authentication successful', self.room_group_name)
								
			else:
				await self.chat_message('error', username, 'Authentication failed', self.room_group_name)
		except Exception as e:
			await self.chat_message('error', 'server', 'Internal server error', self.room_group_name)

	@sync_to_async
	def get_user_from_token(self, token):
		try:
			user = User.objects.filter(auth_token=token).first()
			return user
		except User.DoesNotExist:
			return None