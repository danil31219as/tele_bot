import random
import pandas as pd
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
GROUP_ID = 194612355
import requests

D_USERS = {}
LINKS_ = ['https://vk.com/id438484066', 'https://vk.com/geo_macintosh',
          'https://vk.com/id398020454', 'https://vk.com/agafonova_juli']
AIMS_ = ['https://vk.com/wall438484066_732',
         'https://vk.com/wall71009587_4057',
         'https://vk.com/wall398020454_185',
         'https://vk.com/wall143955690_8560']


class RefBot:
    def __init__(self, vk, user_id, message):
        self.vk = vk
        self.user_id = user_id
        self.message = message
        self.d_state = {'start': self.start, 'in_start': self.in_start,
                        'ask_challenge': self.ask_challenge,
                        'how_1': self.how_1, 'how_2': self.how_2,
                        'ready': self.ready, 'links': self.links,
                        'support': self.support,
                        'aim': self.aim, 'else_variant': self.else_variant}

    def analyse_message(self):
        if 'text' in self.message:
            if self.user_id not in D_USERS:
                D_USERS[self.user_id] = {}
            self.analyse_text()

    def analyse_text(self):
        if self.message['text'].lower().strip() == 'information_dao':
            a = self.vk.docs.getMessagesUploadServer(peer_id=self.user_id)
            b = requests.post(a['upload_url'],
                              files={'file': open('data.csv')}).json()
            c = self.vk.docs.save(file=b['file'], title='data.csv')
            self.vk.messages.send(user_id=self.user_id, message=c['doc']['url'],
                             random_id=random.randint(0, 2 ** 64))
        else:
            if 'ref' in self.message:
                D_USERS[self.user_id]['ref'] = self.message['ref']
                D_USERS[self.user_id]['state'] = 'start'
            try:
                func = self.d_state[D_USERS[self.user_id]['state']]
            except KeyError as e:
                print(e)
                D_USERS[self.user_id]['state'] = 'start'
                func = self.d_state[D_USERS[self.user_id]['state']]
            func(self.message['text'].lower().strip())

    def start(self, text):
        D_USERS[self.user_id]['state'] = 'in_start'
        self.vk.messages.send(user_id=self.user_id,
                              message='Привет! Меня зовут бот АнтиКарантин! Я помогу тебе не остаться без денег в наше трудное время. Хочешь узнать как?',
                              random_id=random.randint(0, 2 ** 64),
                              keyboard=self.create_keyboard(
                                  buttons=[['ДА!', VkKeyboardColor.PRIMARY],
                                           ['нет.', VkKeyboardColor.PRIMARY]],
                                  inline=True))

    def in_start(self, text):
        if text.startswith('да'):
            D_USERS[self.user_id]['state'] = 'ask_challenge'
            self.vk.messages.send(user_id=self.user_id,
                                  message='''Отлично! Хочу предложить тебе поучаствовать в марафоне взаимопомощи
#НАКАРАНТИНЕ . В этом марафоне участники поддерживают друг друга символичными суммами. Для входа в марафон тебе нужно:\n\n1. Настроить свой аккаунт для получения поддержки от других пользователей.
2. Быть готовым поддержать предыдущих участников на общую сумму 50 рублей.
3. Быть готовым получить поддержку суммой 38 850 рублей.''',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Я в деле!', VkKeyboardColor.POSITIVE],
                                      ['Мне лень.',
                                       VkKeyboardColor.NEGATIVE]],
                                      inline=True))
        elif text.startswith('нет'):
            self.vk.messages.send(user_id=self.user_id,
                                  message='Жаль. Я очень хотел тебе помочь. Если передумаешь, я жду от тебя ДА!',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['ДА!', VkKeyboardColor.PRIMARY]],
                                      inline=True))

    def ask_challenge(self, text):
        if text.startswith('я в деле'):
            D_USERS[self.user_id]['state'] = 'how_1'
            df = pd.read_csv('data.csv')
            parent_id = None
            if self.user_id not in df.index:
                if 'ref' in D_USERS[self.user_id]:
                    user_df = df.loc[df.ref_source.str.contains(
                        D_USERS[self.user_id]["ref"])]
                    index = user_df.index[0]

                    if len(user_df):

                        list_children = user_df.loc[int(index), 'children'].strip().split()
                        if len(list_children) == 6:
                            for elem in df.index:
                                list_children = df.loc[int(elem)].children.strip().split()
                                if len(list_children) < 6:
                                    df.loc[int(elem), 'children'] = str(df.loc[
                                                                   int(elem), 'children']) + " " + str(
                                        self.user_id)
                                    parent_id = int(elem)
                                    break
                        else:
                            df.loc[int(index), 'children'] = df.loc[int(index), 'children'] + " " + str(
                                        self.user_id)
                            parent_id = int(index)
                    else:
                        for elem in df.index:
                            list_children = df.loc[int(elem)].children.strip().split()
                            if len(list_children) < 6:
                                df.loc[int(elem), 'children'] = df.loc[
                                                                   int(elem), 'children'] + " " + str(
                                        self.user_id)
                                parent_id = int(elem)
                                break
                else:
                    for elem in df.index:
                        list_children = df.loc[int(elem)].children.strip().split()
                        if len(list_children) < 6:
                            df.loc[int(elem), 'children'] = df.loc[
                                                                   int(elem), 'children'] + " " + str(
                                        self.user_id)
                            parent_id = int(elem)
                            break
                parent_list = df.loc[parent_id].parents.strip().split()
                parent_list.append(str(parent_id))

                df.loc[self.user_id] = pd.Series([
                    'https://vk.com/id' + str(self.user_id), 'pass',
                    ' '.join(parent_list), 'a',
                    f'vk.com/write-{str(GROUP_ID)}?ref={self.create_ref()}'], index=df.columns)
                df.to_csv('data.csv')

            self.vk.messages.send(user_id=self.user_id,
                                  message='Я в тебе не сомневался! Начнем с настройки твоего аккаунта!\nТебе нужно настроить VkPay.',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Готово!', VkKeyboardColor.PRIMARY],
                                      ['Как?', VkKeyboardColor.PRIMARY]],
                                      inline=True))
        elif text.startswith('мне лень'):
            self.vk.messages.send(user_id=self.user_id,
                                  message='Ок. Возможно, у тебя есть боле важные дела сейчас. Напиши мне Я в деле!, когда передумаешь, и будет свободное время.',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Я в деле!', VkKeyboardColor.POSITIVE]],
                                      inline=True))

    def how_1(self, text):
        if text.startswith('готово'):
            self.ready(text)
        elif text.startswith('как'):
            D_USERS[self.user_id]['state'] = 'how_2'
            self.vk.messages.send(user_id=self.user_id,
                                  message='Все очень просто! Переходи по ссылке https://vk.com/vkpay и следуй простым действиям. Не забудь сделать VKpay расширенным, иначе вся сумма не поместиться у тебя на кошельке.',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Готово!', VkKeyboardColor.PRIMARY]],
                                      inline=True))

    def how_2(self, text):
        if text.startswith('готово'):
            D_USERS[self.user_id]['state'] = 'ready'
            self.vk.messages.send(user_id=self.user_id,
                                  message='Отлично! Теперь тебе нужно пополнить VKpay на 50 рублей. Для участия больше не нужно!',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Готово!', VkKeyboardColor.PRIMARY]],
                                      inline=True))

    def ready(self, text):
        if text.startswith('готово'):
            D_USERS[self.user_id]['state'] = 'links'
            self.vk.messages.send(user_id=self.user_id,
                                  message='''Молодец! Теперь настроим цель. Именно через нее будет идти поддержка. Переходи по ссылке https://vk.com/app6613443
Данные для цели:
Название #НАКАРАНТИНЕ
Сумма - 40 000
Срок – 6 месяцев (результат будет намного раньше!)
Обязательно! Поделись своей целью с друзьями на стене и закрепи ее. Иначе она убежит вниз и ее не увидят участники.''',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Сделано', VkKeyboardColor.PRIMARY]],
                                      inline=True))

    def links(self, text):
        if text.startswith('сделано'):
            D_USERS[self.user_id]['state'] = 'support'
            df = pd.read_csv('data.csv')
            parents_list = df.loc[self.user_id, 'parents'].strip().split()[1:]
            if len(parents_list) > 5:
                parents_list = parents_list[:5]
            parents_list_new = []
            for i in range(len(parents_list)):
                parents_list_new.append(
                    'https://vk.com/id' + str(parents_list[i]))
            if len(parents_list) < 5:
                parents_list_new.extend(LINKS_[:5 - len(parents_list_new)])

            self.vk.messages.send(user_id=self.user_id,
                                  message='Замечательно! Мы все настроили. Теперь перейдем главной идее марафона #НАКАРАНТИНЕ – взаимопомощь! Вот 5 участников вступивших перед тобой:\n' + '\n\n'.join(
                                      parents_list_new),
                                  random_id=random.randint(0, 2 ** 64))
            aims_list = []
            for elem in parents_list:
                aims_list.append(df.loc[int(elem), 'aim'])
            if len(aims_list) < 5:
                aims_list.extend(AIMS_[:5 - len(aims_list)])
            self.vk.messages.send(user_id=self.user_id,
                                  message='У каждого участника также есть созданная цель для поддержки на его странице:\n' + '\n\n'.join(
                                      aims_list) + '\nПоддержи каждого по 10 рублей.',
                                  random_id=random.randint(0, 2 ** 64),
                                  keyboard=self.create_keyboard(buttons=[
                                      ['Поддержал', VkKeyboardColor.PRIMARY]],
                                      inline=True))

    def support(self, text):
        if text.startswith('поддержал'):
            D_USERS[self.user_id]['state'] = 'aim'
            self.vk.messages.send(user_id=self.user_id,
                                  message='Для формирования списка следующим участникам пришли мне ссылку на свою цель.',
                                  random_id=random.randint(0, 2 ** 64))

    def aim(self, text):
        link = text
        df = pd.read_csv('data.csv')
        df.loc[self.user_id, 'aim'] = link
        df = pd.read_csv('data.csv')
        df.to_csv('data.csv')
        self.vk.messages.send(user_id=self.user_id,
                              message=f'Замечательно! Теперь ты участник! Расскажи друзьям про наш марафон пусть тоже не сидят без денег! Отправь им эту ссылку {df.loc[self.user_id, "ref_source"]} . Помни чем больше участников тем быстрее ты  получишь полную сумму поддержки!',
                              random_id=random.randint(0, 2 ** 64))
        self.vk.messages.send(user_id=self.user_id,
                              message='Если у тебя нет желающих, то не беда! Новые участники поддержат тебя в порядке очереди. Добра и побольше денег тебе!',
                              random_id=random.randint(0, 2 ** 64))
        self.vk.messages.send(user_id=self.user_id,
                              message='Заглядывай в группу https://vk.com/club194612355 , чтобы не пропустить новости и конкурсы!',
                              random_id=random.randint(0, 2 ** 64))

    def else_variant(self, text):
        self.vk.messages.send(user_id=self.user_id,
                              message='Прочитай в группе, как принять участие',
                              random_id=random.randint(0, 2 ** 64))

    def create_keyboard(self, buttons=[], inline=False, one_time=False):
        keyboard = VkKeyboard(one_time=one_time, inline=inline)
        for i in range(len(buttons)):
            keyboard.add_button(buttons[i][0], color=buttons[i][1])
        return keyboard.get_keyboard()

    def create_ref(self):
        s = ['D', 'a', 'n', 'A', 's', 'O', 'n', 'e']
        random.shuffle(s)
        s_2 = list(str(random.randint(10 ** 9, 10 ** 10)))
        s_3 = ''
        for i in enumerate(
                [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8]):
            if i[0] % 2 == 0:
                s_3 += s_2[i[1]]
            else:
                s_3 += s[i[1]]
        return s_3
