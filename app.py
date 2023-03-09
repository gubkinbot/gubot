import telebot
import openai
import yaml

with open('keys.yaml', 'r') as f:
    secrets = yaml.safe_load(f)

TG_TOKEN = secrets.get('TG_TOKEN')
OPENAI_KEY = secrets.get('OPENAI_KEY')

openai.api_key = OPENAI_KEY

dialogues = {'user': None}

bot = telebot.TeleBot(TG_TOKEN)


def add_message(role, ai_message, old_array):
    if old_array == None:
        old_array = [{"role": "system", "content": "Знаю совеременные технологии добычи нефти и газа, машинное обучение. Заинтересован в интеллектуальном развитии сотрудников ЛУОК."}]
    old_array.append({"role": f"{role}", "content": f"{ai_message}"})
    return old_array

def get_answer(ai_message):
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=ai_message)
        return response['choices'][0]['message']['content']
    except:
        return 'Ошибка связи с Open AI. Скорее всего дело в слишком частых запросах. Повторите попытку позже.'


def check_user(user_id):
    try:
        dialogues[user_id]
        return len(dialogues[user_id])
    except:
        dialogues.update([[user_id,  None]])
        return 0
        
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Добро пожаловать! Готов ответить на любые вопросы. Лучше всего понимаю английский язык, но и на русском что-то могу. Основан на ChatGPT, аватарка Midjourney')

@bot.message_handler(commands=['reboot'])
def reset(message):
    dialogues.update([[message.from_user.id,  None]])
    bot.reply_to(message, "Начнем с чистого листа!")

@bot.message_handler(commands=['about'])
def about(message):
    bot.reply_to(message, "Можно спрашивать что угодно. Например, какие есть способы снижение скорости газа в трубопроводе, состав газа, как оптимизировать добычу и многое-многое другое. Лучше всего работает на английском языке.")   

@bot.message_handler(func=lambda message: True)
def echo(message):
    length = check_user(message.from_user.id) + 2
    tmp_message = add_message('user', message.text, dialogues[message.from_user.id])
    answer = get_answer(tmp_message)
    bot.reply_to(message, f'[{length}/20] {answer}')
    dialogues[message.from_user.id] = add_message('assistant', answer, dialogues[message.from_user.id])
    if length > 20:
        dialogues.update([[message.from_user.id,  None]])
        bot.reply_to(message, 'Ваш разговор затянулся. Вынужден его прервать. Вы можете начать разговор сначала.')
    
bot.polling()