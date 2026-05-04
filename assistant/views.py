from django.shortcuts import render
from django.http import JsonResponse
from .ai_engine import TechShopAssistant

assistant = TechShopAssistant()


def chat_view(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    history = request.session['chat_history']
    return render(request, 'assistant/chat.html', {'history': history})


def chat_api(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Сообщение пустое'}, status=400)

        response = assistant.process_message(message)

        # Save to session history
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []
        request.session['chat_history'].append({'role': 'user', 'text': message})
        request.session['chat_history'].append({'role': 'assistant', 'text': response})
        # Keep last 20 messages
        request.session['chat_history'] = request.session['chat_history'][-20:]
        request.session.modified = True

        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def clear_chat(request):
    request.session['chat_history'] = []
    request.session.modified = True
    return JsonResponse({'success': True})
