# /pong/game/views.py

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import Player, Tournoi, Match
from .utils import create_player, create_tournoi, create_match
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.http import HttpResponse

import json
import uuid

def trigger_error(request):
    raise ValueError("This is a test error to generate a 500 response.")

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def check_user_exists(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'exists': True})
        return JsonResponse({'exists': False})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            token = get_or_create_token(user)
            return JsonResponse({'registered': True, 'token': token})
        return JsonResponse({'registered': False, 'error': 'User already exists'})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def authenticate_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '')
            password = data.get('password', '')
            user = authenticate(username=username, password=password)
            if user is not None:
                token = get_or_create_token(user)
                return JsonResponse({'authenticated': True, 'token': token, 'user_id': user.id})
            else:
                return JsonResponse({'authenticated': False}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_or_create_token(user):
    if not user.auth_token:
        while True:
            token = str(uuid.uuid4())
            if not User.objects.filter(auth_token=token).exists():
                user.auth_token = token
                user.save()
                break
    return user.auth_token

def match_list_json(request):
    matches = Match.objects.all()
    data = {
        'matches': list(matches.values(
            'id', 'player1__name', 'player2__name', 'score_player1', 'score_player2',
            'winner__name', 'nbr_ball_touch_p1', 'nbr_ball_touch_p2', 'duration', 'date',
            'is_tournoi', 'tournoi__name'
        ))
    }
    return JsonResponse(data)

def player_list_json(request):
    players = Player.objects.all()
    
    data = {
        'players': list(players.values(
            'id', 'name', 'total_match', 'total_win', 'p_win',
            'm_score_match', 'm_score_adv_match', 'best_score',
            'm_nbr_ball_touch', 'total_duration', 'm_duration',
            'num_participated_tournaments', 'num_won_tournaments'
        ))
    }
    return JsonResponse(data)

def get_tournoi_data(tournoi):
    return {
        "id": tournoi.id,
        "name": tournoi.name,
        "nbr_player": tournoi.nbr_player,
        "date": tournoi.date,
        "winner": {
            "id": tournoi.winner.id,
            "name": tournoi.winner.name
        } if tournoi.winner else None
    }

def tournoi_list_json(request):
    tournois = Tournoi.objects.select_related('winner').all()  # Charge les données du gagnant
    tournois_data = [get_tournoi_data(tournoi) for tournoi in tournois]
    return JsonResponse({"tournois": tournois_data})


import os
from web3 import Web3
import time

provider = Web3.HTTPProvider(os.getenv('WEB3_PROVIDER'))
web3 = Web3(provider)
eth_gas_price = web3.eth.gas_price/1000000000
print(eth_gas_price)

contract_address = os.getenv('CONTRACT_ADDRESS')
contract_abi = [{"inputs": [{"internalType": "uint256","name": "_timecode","type": "uint256"},{"internalType": "string[]","name": "_player_list","type": "string[]"},{"internalType": "string","name": "_winner","type": "string"}],"name": "addTournament","outputs": [],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"stateMutability": "nonpayable","type": "constructor"},{"inputs": [],"name": "getAllTournaments","outputs": [{"components": [{"internalType": "uint256","name": "id","type": "uint256"},{"internalType": "uint256","name": "timecode","type": "uint256"},{"internalType": "string[]","name": "player_list","type": "string[]"},{"internalType": "string","name": "winner","type": "string"}],"internalType": "struct PongTournament.Tournament[]","name": "","type": "tuple[]"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "_id","type": "uint256"}],"name": "getTournament","outputs": [{"components": [{"internalType": "uint256","name": "id","type": "uint256"},{"internalType": "uint256","name": "timecode","type": "uint256"},{"internalType": "string[]","name": "player_list","type": "string[]"},{"internalType": "string","name": "winner","type": "string"}],"internalType": "struct PongTournament.Tournament","name": "","type": "tuple"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "owner","outputs": [{"internalType": "address","name": "","type": "address"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "tournamentCount","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "","type": "uint256"}],"name": "tournaments","outputs": [{"internalType": "uint256","name": "id","type": "uint256"},{"internalType": "uint256","name": "timecode","type": "uint256"},{"internalType": "string","name": "winner","type": "string"}],"stateMutability": "view","type": "function"}]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def write_data(player_list, winner):
    if (os.getenv('WEB3_PROVIDER') != "https://sepolia.infura.io/v3/60e51df7c97c4f4c8ab41605a4eb9907"):
        return
    timecode = int(time.time())
    account = os.getenv('WEB3_ACCOUNT')
    private_key = os.getenv('PRIVATE_KEY')

    print(contract_address, account, private_key)
    print(timecode, player_list, winner)

    nonce = web3.eth.get_transaction_count(account)
    print(web3.to_wei(eth_gas_price, 'gwei'))
    print(nonce)
    transaction = contract.functions.addTournament(timecode, player_list, winner).build_transaction({
        'chainId': 11155111,  # ID de la chaîne Sepolia
        'gas': 2000000,
        'gasPrice': web3.to_wei(eth_gas_price, 'gwei'),
        'nonce': nonce
    })

    # Signature de la transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # Envoi de la transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print("Transaction hash:", web3.to_hex(tx_hash))

    # Attente de la confirmation de la transaction
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction receipt:", tx_receipt)
