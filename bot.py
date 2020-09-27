import discord
from discord.ext import commands
from Cybernator import Paginator as pag
import asyncio
import random
import re
import requests
from massive.discord import discord_massive
import jishaku
import sqlite3
import time

PREFIX = '/'

def is_owner(ctx):
    return ctx.message.author.id == 451410256736550918

client = commands.Bot( command_prefix = PREFIX )
client.remove_command( 'help' )

client.load_extension('jishaku')

#Экономика
connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
	cursor.execute("""CREATE TABLE IF NOT EXISTS users(
		name TEXT,
		id INT,
		cash BIGINT,
		stafs INT,
		warning INT,
		server_id INT
	)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
		role_id INT,
		id INT,
		cost BIGINT
	)""")

	for guild in client.guilds:
		for member in guild.members:
			if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, {member.guild.id})")
			else:
				pass

	connection.commit()
	print( 'BOT IS READY')

@client.event
async def on_member_join(member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0, {member.guild.id})")
		connection.commit()
	else:
		pass

@client.command(aliases = ['balance', 'cash'])
async def __balance(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Личный кошелек:',description = f"""Баланс пользователя **{ctx.author.mention}** составляет **`{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:\n **Сумма ваших штрафов:** `{cursor.execute("SELECT stafs FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}`** :military_medal:""", colour = discord.Colour.gold()))	
	else:
		await ctx.send(embed = discord.Embed(title = f'Кошелек пользователя: {member.display_name}',description = f"""Баланс пользователя **{member.mention}** составляет **`{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :military_medal: \n **Сумма его штрафов** `{cursor.execute("SELECT stafs FROM users WHERE id = {}".format(member.id)).fetchone()[0]}`** :military_medal:""", colour = discord.Colour.gold()))

#@client.command(aliases = ['rank'])
#async def __rank(ctx, member: discord.Member = None):
#	if member is None:
#	 	await ctx.send(embed = discord.Embed(description = f"""Уровень пользователя **{ctx.author}** составляет **{cursor.execute("SELECT lvl FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}**""", colour = discord.Colour.gold()))
#	else:
#		await ctx.send(embed = discord.Embed(description = f"""Уровень пользователя **{member}** составляет **{cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}**""", colour = discord.Colour.gold()))

@client.command(aliases = ['astaf', 'afine'])
@commands.has_permissions(administrator = True)
async def __afine(ctx, member: discord.Member = None, amount: int = None):
	emb = discord.Embed(title = '**Discord >> штрафы!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Выписал штраф!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**В размере:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(759092548320624711)

	if member is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите пользователя которому вы хотите выписать штраф**', delete_after = 5)
	elif amount is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите сумму которую вы хотите выписать в виде штрафа**', delete_after = 5)
	elif amount < 1:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, укажите сумму штрафа больше чем 1!**', delete_after = 5)
	else:
		await ctx.send(embed = discord.Embed(title = 'Штраф | Fine', description = f'**Модератор** {ctx.author.mention}**, выписал штраф пользователю** {member.mention}**, в размере:** `{amount}` :military_medal:', colour = discord.Colour.gold()))
		await channel.send(embed = emb)
		cursor.execute("UPDATE users SET stafs = stafs + {} WHERE id = {}".format(amount, member.id))
		connection.commit()

@client.command(aliases = ['unstaf', 'unfine'])
@commands.has_permissions(administrator = True)
async def __unfine(ctx, member: discord.Member = None, amount: int = None):
	emb = discord.Embed(title = '**Discord >> штрафы!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Списал штраф!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**В размере:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(759092548320624711)

	if member is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите пользователя у которого вы хотите списать штраф**', delete_after = 5)
	elif amount is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите сумму которую вы хотите списать у пользователя в виде штрафа**', delete_after = 5)
	elif amount < 1:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите сумму больше чем 1**', delete_after = 5)
	else:
		await ctx.send(embed = discord.Embed(title = 'Штраф | Fine', description = f'**Модератор** {ctx.author.mention}**, списал штраф пользователю** {member.mention}**, в размере:** `{amount}` :military_medal:', colour = discord.Colour.gold()))
		await channel.send(embed = emb)
		cursor.execute("UPDATE users SET stafs = stafs - {} WHERE id = {}".format(amount, member.id))
		connection.commit()

@client.command(aliases = ['pstaf', 'pfine'])
async def __pfine(ctx, amount: int = None):
	if amount is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите сумму которую вы хотите заплатить за штраф**', delete_after = 5)
	elif amount < 1:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention}**, обязатльно укажите сумму больше чем 1**', delete_after = 5)
	elif cursor.execute("SELECT stafs FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, у вас недостаточно средст для оплаты такой суммы штрафа!`**', delete_after = 5)
	else:
		await ctx.send(embed = discord.Embed(title = 'Штраф | Fine', description = f'{ctx.author.mention}**, вы оплатили свой штраф в размере:** `{amount}` :military_medal:', colour = discord.Colour.gold()))
		cursor.execute("UPDATE users SET stafs = stafs - {} WHERE id = {}".format(amount, ctx.author.id))
		cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
		connection.commit()

@client.command(aliases = ['staf', 'fine'])
async def __fine(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ваши штрафы | Your fine', description = f'**Сумма всех ваших штрафов составляет:** `{cursor.execute("SELECT stafs FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold()))
	else:
		await ctx.send(embed = discord.Embed(title = f'Штрафы пользователя {member.display_name} | Fine users', description = f'**Сумма всех штрафов пользователя** {member.mention} **составляет:** `{cursor.execute("SELECT stafs FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold()))

@client.command(aliases = ['gmoney', 'amoney', 'gcash'])
@commands.has_permissions( administrator = True )
async def __amoney(ctx, member: discord.Member = None, amount: int = None):
	emb = discord.Embed(title = '**Discord >> обновление баланса пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Выдал средства!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**В размере:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327728188981448)

	if member is None:
		await ctx.send(f"**`[ERROR]`{ctx.author}`, укажите пользователя которому вы хотите добавить определенную сумму`**", delete_after = 5)
	else:
		if amount is None:
			await ctx.send(f"**`[ERROR]`{ctx.author}`, укажите сумму, которую желаете добавить!`**", delete_after = 5)
		elif amount < 1:
			await ctx.send(f"**`[ERROR]`{ctx.author}`, укажите сумму больше 1`**", delete_after = 5)
		else:
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			connection.commit()
			await ctx.send(embed = discord.Embed(title = 'Выдача валюты', description = f'**Администратор** {ctx.author.mention} **выдал пользователю** {member.mention}**, валюту в размере:** `{amount}`:military_medal:\n **Его баланс теперь состовляет** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold()))

			await channel.send(embed = emb)
			

@client.command(aliases = ['tmoney', 'dmoney', 'dcash'])
@commands.has_permissions( administrator = True )
async def __tmoney(ctx, member: discord.Member = None, amount = None):
	emb = discord.Embed(title = '**Discord >> обновление баланса пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Отнял средства!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**В размере:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327728188981448)

	if member is None:
		await ctx.send(f"**`[ERROR]`{ctx.author}, `укажите пользователя у которого хотите отнять определенную сумму`**", delete_after = 5)
	else:
		if amount is None:
			await ctx.send(f"**`[ERROR]`{ctx.author}, `укажите сумму, которую желаете отнять!`**", delete_after = 5)
		elif amount == 'all':
			cursor.execute("UPDATE users SET cash = cash = {} WHERE id = {}".format(0, member.id))
			connection.commit()
			await ctx.send(embed = discord.Embed( title = 'Обнуление баланса пользователя', description = f'**Администратор** {ctx.author.mention} **обнулил баланс пользователя** {member.mention} **за нарушения правил.**\n **Его баланс теперь составляет** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :tickets:', colour = discord.Colour.gold()))
			await channel.send(f"{ctx.author.mention},  обнулил баланс пользователя {member.mention}")
		elif int(amount) < 1:
			await ctx.send(f"**`[ERROR]`{ctx.author}`, укажите сумму больше 1`**", delete_after = 5)
		else:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
			connection.commit()
			await ctx.message.add_reaction('✅')

			await ctx.send(embed = discord.Embed( title = 'Списание средств с баланса', description = f'**Администратор** {ctx.author.mention} **списал со счета пользователя** {member.mention} **сумму в размере** `{amount}` :military_medal:\n **Его баланс теперь составляет** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :tickets:',colour = discord.Colour.gold()))
			await channel.send(embed = emb)
			await ctx.message.add_reaction('✅')


@client.command(aliases = ['add-shop'])
@commands.has_permissions( administrator = True )
async def __add_shop(ctx, role: discord.Role = None, cost: int = None):
	emb = discord.Embed(title = '**Discord >> обновление магазина!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Выставил роль на продажу!`**' )
	emb.add_field( name = '**Роль:**', value = f'{ctx.guild.get_role(role.id).mention}' )
	emb.add_field( name = '**И установил стоимость:**', value = f'**`{cost}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757328931497181285)

	if role is None:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, укажите роль которую хотите выставить на продажу!`**', delete_after = 5)
	else:
		if cost is None:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, пожалуйста укажите стоимость для данной роли!`**', delete_after = 5)
		elif cost < 0:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, стоимость роли не может быть такой маленькой!`**', delete_after = 5)
		else:
			cursor.execute('INSERT INTO shop VALUES ({}, {}, {})'.format(role.id, ctx.guild.id, cost))
			connection.commit()
			await ctx.message.add_reaction('✅')
			await channel.send(embed = emb)

@client.command(aliases = ['remove-shop'])
@commands.has_permissions( administrator = True )
async def __remove_shop(ctx ,role: discord.Role = None):
	emb = discord.Embed(title = '**Discord >> обновление магазина!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Удалил роль с продажи!`**' )
	emb.add_field( name = '**Роль:**', value = f'{ctx.guild.get_role(role.id).mention}' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757328931497181285)

	if role is None:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, укажите роль для удаления ее из магазина!`**', delete_after = 5)
	else:
		cursor.execute('DELETE FROM shop WHERE role_id = {}'.format(role.id))
		connection.commit()

		await ctx.message.add_reaction('✅')
		await channel.send(embed = emb)

@client.command(aliases = ['shop'])
async def __shop(ctx):
	embed = discord.Embed(title = ':white_flower: Магазин уникальных ролей :white_flower:')

	for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
		if ctx.guild.get_role(row[0]) != None:
			embed.add_field(
				name = f'Стоимость {row[1]} :military_medal:',
				value = f'Вы приобретёте роль {ctx.guild.get_role(row[0]).mention}',
				inline = False
			)
		else:
			pass

	await ctx.send(embed = embed)

@client.command(aliases = ['buy', 'buy-role'])
async def __buy(ctx, role: discord.Role = None):
	emb = discord.Embed(title = '**Discord >> покупка роли!**')
	emb.add_field(name = f'**Пользователь**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Купил роль из магазина!`**' )
	emb.add_field( name = '**Купленная роль:**', value = f'{ctx.guild.get_role(role.id).mention}' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757329255414759536)

	if role is None:
		await ctx.send(f'{ctx.author.mention}, укажите роль котрую вы хотите приобрести!')
	else:
		if role in ctx.author.roles:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, у вас уже имеется данная роль!`**', delete_after = 5 )
		elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, у вас недостаточно средст для покупки данной роли!`**', delete_after = 5)
		else:
			await ctx.author.add_roles(role)
			cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
			connection.commit()

			await ctx.message.add_reaction('✅')
			await channel.send(embed = emb)


@client.command(aliases =['pay'])
async def __pay(ctx, member: discord.Member = None, amount: int = None):
	emb = discord.Embed(title = '**Discord >> обновление баланса пользователя!**')
	emb.add_field(name = f'**Пользователь:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Передал средства!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**В размере:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327728188981448)

	if member is None:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, укажите пользователя которому вы хотите передать монеты!`**', delete_after = 5)
	elif member.id == ctx.author.id:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, вы не можете передавать деньги самому себе!`**', delete_after = 5)
	else:
		if amount is None:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, пожалуйста количество монет для передачи!`**', delete_after = 5)
		elif amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, у вас недостаточно средст для передачи такой суммы денег!`**', delete_after = 5)
		else:
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount), member.id))
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			connection.commit()
			await ctx.send(embed = discord.Embed(title = 'Передача валюты', description = f'{ctx.author.mention}, **вы передали пользователю** {member.mention} **валюту в размере** `{amount}` :military_medal:\n **Его баланс теперь** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold()))
			await channel.send(embed = embed)

@commands.cooldown(1, 30, commands.BucketType.user)
@client.command(aliases = ['casino'])
async def __casino(ctx, amount: int = None):
	af = random.choices([1, 2, 3, 4, 5], weights=[50, 50, 10, 5, 0.001])[0]
	f = 150000
	ar = 756931456198115358
	if amount is None:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, пожалуйста количество монет для ставки!`**', delete_after = 5)
	elif amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, у вас недостаточно средств!`**', delete_after = 5)
	elif amount > f:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, сумма вашей ставки не может быть больше чем 150.000!`** :tickets:', delete_after = 5)
	else:
		if af == 1:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			connection.commit()

			await ctx.send(embed = discord.Embed(description = f'**{ctx.author.display_name}, ваша ставка успешно принята! Дождитесь результатов.**', colour = discord.Colour.gold()), delete_after = 5)
			await asyncio.sleep(5)

			emb = discord.Embed(title = 'Подпольное казино', description = f'**{ctx.author.mention}, к сожалению вам сегодня не повезло,вы проиграли!\n Ваш баланс теперь состовляет:** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.red())
			await ctx.send(embed = emb)
		elif af == 2:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount * 2), ctx.author.id))
			connection.commit()

			await ctx.send(embed = discord.Embed(description = f'**{ctx.author.display_name}, ваша ставка успешно принята! Дождитесь результатов.**', colour = discord.Colour.gold()), delete_after = 5)
			await asyncio.sleep(5)

			emb = discord.Embed(title = 'Подпольное казино', description = f'**{ctx.author.mention}, поздравляем вам сегодня повезло,вы удвоили свою ставку в 2 раза! \n Ваш баланс теперь состовляет:** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.green())
			await ctx.send(embed = emb)
		elif af == 3:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount * 5), ctx.author.id))
			connection.commit()

			await ctx.send(embed = discord.Embed(description = f'**{ctx.author.display_name}, ваша ставка успешно принята! Дождитесь результатов.**', colour = discord.Colour.gold()), delete_after = 5)
			await asyncio.sleep(5)

			emb = discord.Embed(title = 'Подпольное казино', description = f'**{ctx.author.mention}, Ничего себе вы настолько везучий,что увеличили вашу ставку аж в 5 раз \n Ваш баланс теперь состовляет:** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold())
			await ctx.send(embed = emb)
		elif af == 4:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount * 10), ctx.author.id))
			connection.commit()

			await ctx.send(embed = discord.Embed(description = f'**{ctx.author.display_name}, ваша ставка успешно принята! Дождитесь результатов.**', colour = discord.Colour.gold()), delete_after = 5)
			await asyncio.sleep(5)

			emb = discord.Embed(title = 'Подпольное казино', description = f'**{ctx.author.mention}, НИЧЕГО себе фортуна сегодня явно на вашей стороне вы увеличили свою ставку аж в 10 раз! \n Ваш баланс теперь состовляет:** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold())
			await ctx.send(embed = emb)
		elif af == 5:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), ctx.author.id))
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(int(amount * 100), ctx.author.id))
			connection.commit()

			await ctx.send(embed = discord.Embed(description = f'**{ctx.author.display_name}, ваша ставка успешно принята! Дождитесь результатов.**', colour = discord.Colour.gold()), delete_after = 5)
			await asyncio.sleep(5)

			emb = discord.Embed(title = 'Подпольное казино', description = f'**{ctx.author.mention}, ЭТО ПРОСТО НЕВЕРОЯТНО похоже что вы сорвали джек-пот и увеличили вашу ставку аж в 100 раз! \n Ваш баланс теперь состовляет:** `{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}` :military_medal:', colour = discord.Colour.gold())
			await ctx.send(embed = emb)
		else:
			await ctx.send(embed = discord.Embed(description = 'Воу Воу не надо так быстро использовать эту команду!'))


@client.command(aliases = ['add-rep'])
@commands.has_permissions( administrator = True )
async def __add_rep(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, укажите пользователя которому вы хотите выдать репутацию!`**', delete_after = 5)
	else:
		if member.id == ctx.author.id:
			await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, вы не можете выдавать репутацию самому себе!`**', delete_after = 5)
		else:
			cursor.execute('UPDATE users SET rep = rep + {} WHERE id = {}'.format(1, member.id))
			connection.commit()

			await ctx.message.add_reaction('✅')

@client.command(aliases = ['rep'])
async def __rep(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = 'Ваша репутация:',
		description = f"""Репутация пользователя **{ctx.author.display_name}** составляет **{cursor.execute("SELECT rep FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}**"""
		))
	else:
		await ctx.send(embed = discord.Embed(title = f'Репутация пользователя {member.display_name}',
		description = f"""Репутация пользователя **{member.display_name}** составляет **{cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0]}**"""
		))

@client.command(pass_context = True)
async def topcash(ctx):
	emb = discord.Embed(title = ':tickets: Топ 10 самых богатых людей сервера! :tickets:')
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )

	counter = 0

	for row in cursor.execute("SELECT name, cash FROM users WHERE server_id = {} ORDER BY cash DESC LIMIT 10".format(ctx.guild.id)):
		counter += 1 
		emb.add_field( name = f'# {counter} | {row[0]}', value = f'Баланс: {row[1]} :military_medal:', inline = False)

	await ctx.send(embed = emb)

@client.command(aliases = ['warn'])
@commands.has_permissions(administrator = True)
async def __warn(ctx, member: discord.Member, amount: int = None):
	emb = discord.Embed(title = '**Discord >> предупреждение!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Выдал предупреждение!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.add_field( name = '**С причиной:**', value = f'**`{amount}`** :military_medal:' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327510362128394)

	if member is None: 
		await ctx.send('**`[ERROR]` Укажите пользователя которому вы хотите выдавать наказание!**', delete_after = 5)
	elif member.id == ctx.author.id:
		await ctx.send(f'**`[ERROR]`{ctx.author.mention}`, вы не можете выдавать предупреждение самому себе!`**', delete_after = 5)
	else:
		if amount is None:
			await ctx.send(f'**`[ERROR]` {ctx.author.mention} обязатльно укажите причину выдачи наказания!**', delete_after = 5)
		else:
			cursor.execute('UPDATE users SET warning = warning + {} WHERE id = {}'.format(1, member.id))
			connection.commit()
			await ctx.send(embed = discord.Embed(title = 'Предупреждение участника сервера.', description = f'**Модератор** {ctx.author.mention} **выдал предупреждение пользователю** {member.mention} **теперь количество его предупреждений состовляет :** `{cursor.execute("SELECT warning FROM users WHERE id = {}".format(member.id)).fetchone()[0]}`', colour = discord.Colour.gold()))
			await channel.send(embed = embed)

@client.command(aliases = ['warnlog'])
async def __warnlog(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(title = f'Предупреждения пользователя {ctx.author.display_name}', description = f'**Количество предупреждений пользователя** {ctx.author.mention} **состовляет** `{cursor.execute("SELECT warning FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}`', colour = discord.Colour.gold()))
	else:
		await ctx.send(embed = discord.Embed(title = f'Предупреждения пользователя {member.display_name}', description = f'**Количество предупреждений пользователя** {member.mention} **состовляет** `{cursor.execute("SELECT warning FROM users WHERE id = {}".format(member.id)).fetchone()[0]}`', colour = discord.Colour.gold()))

@client.command(aliases = ['unwarn'])
@commands.has_permissions(administrator = True)
async def __unwarn(ctx, member: discord.Member = None):
	emb = discord.Embed(title = '**Discord >> снятие предупреждений!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Снял предупреждение!`**' )
	emb.add_field( name = '**Пользователю:**', value = f'{member.mention}' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327510362128394)

	if member is None:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention} **обязатльно укажите пользователя которому вы хотите снять предупреждение!**', delete_after = 5)
	elif member.id == ctx.author.id:
		await ctx.send(f'**`[ERROR]`** {ctx.author.mention} **вы не можете снять предупреждение самому себе!**', delete_after = 5)
	else:
		cursor.execute('UPDATE users SET warning = warning - {} WHERE id = {}'.format(1, member.id))
		connection.commit()
		await ctx.send(embed = discord.Embed(title = 'Снятие предупреждения', description = f'**Модератор** {ctx.author.display_name} **снял пользователю** {member.display_name} **предупреждение в размере `1`! теперь количество его предупреждений состовляет:** `{cursor.execute("SELECT warning FROM users WHERE id = {}".format(member.id)).fetchone()[0]}`', colour = discord.Colour.gold()))
		await channel.send(embed = embed)

@client.event
async def on_command_error( ctx, error ):
	pass

@client.command( pass_context = True )

async def hello( ctx ):
	author = ctx.message.author

	await ctx.send( f" { author.mention } привет,не читай это!" )
 
# очистка чата
@client.command( pass_context = True )
@commands.has_permissions( administrator  = True )
	
async def clear( ctx, amount : int ):
	await ctx.channel.purge( limit = amount )
	await ctx.send( embed = discord.Embed( description = f':white_check_mark: Удалено { amount } сообщений.',colour = discord.Colour.green() ), delete_after = 5 )

# кик
@client.command( pass_context = True )
@commands.has_permissions( administrator  = True )

async def kick( ctx,member : discord.Member, *,reason = None ):
	emb = discord.Embed( title = 'Беда,член семьи был выгнан с сервера!', colour = discord.Colour.red() )
	await ctx.channel.purge( limit = 1 )

	await member.kick( reason = reason )

	emb.set_author( name = member.name, icon_url = member.avatar_url )
	emb.add_field( name = 'Кик пользователя', value = 'Был выгнан пользователь {}'.format( member.mention ))
	emb.add_field( name = f'Выдал наказание: Technical Administrator Discord | VK', value = 'Причина:{}'.format(reason)) 
	emb.set_footer( text = 'Все права защищены by Кодик', icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> кик пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Кикнул | Выгнал!`**' )
	emb.add_field( name = '**Пользователя:**', value = f'{member.mention}' )
	emb.add_field( name = f'Причина:', value = '{}'.format(reason))
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327564778766455)
	await channel.send(embed = emb)

# бан
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def ban( ctx,member: discord.Member, *,reason = None ):
	emb = discord.Embed( title = '`Discord` >> Блокировка учетной записи пользователя', colour = discord.Colour.red() )
	await ctx.channel.purge( limit = 1 )

	await member.ban( reason = reason )

	emb.set_author( name = member.name, icon_url = member.avatar_url )
	emb.add_field( name = 'Блокировка пользователя', value = 'Был заблокирован пользователь {}'.format( member.mention ))
	emb.add_field( name = f'заблокирован пользователь:', value = '{}'.format(member.mention)) 
	emb.add_field( name = f'Выдал наказание:', value = '{}'.format(ctx.author.mention))
	emb.add_field( name = f'Причина:', value = '{}'.format(reason)) 
	emb.set_footer( text = 'Все права защищены by Кодик', icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> Блокировка учетной записи!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`Забанил!`**' )
	emb.add_field( name = '**Пользователя:**', value = f'{member.mention}' )
	emb.add_field( name = f'Причина:', value = '{}'.format(reason)) 
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757327218211946507)
	await channel.send(embed = emb)

# разбан
@client.command( pass_context = True )
@commands.has_permissions( administrator = True )

async def unban( ctx, *, member ):
	await ctx.channel.purge( limit = 1 )

	banned_users = await ctx.guild.bans()

	for ban_entry in banned_users:
		user = ban_entry.user

		await ctx.guild.unban( user )
		await ctx.send( f'был разбанен { user.mention } ' )

	
		return



# хелп 
@client.command( pass_context = True )

async def thelp( ctx ):
	emb = discord.Embed( title = 'Информация о командах', description = 'Вы сможете узнать описание команд', colour = discord.Colour.red(), url = 'http://s3287.pcdn.co/wp-content/uploads/2010/10/Resources.jpeg' )

	emb.add_field( name = '{}clear'.format( PREFIX ), value = 'Очистка чата.')
	emb.add_field( name = '{}kick'.format( PREFIX ), value = 'Выгнать участника.')
	emb.add_field( name = '{}ban'.format( PREFIX ), value = 'Забанить участника.')
	emb.add_field( name = '{}unban'.format( PREFIX ), value = 'Разбанить участника.')
	emb.add_field( name = '{}help'.format( PREFIX ), value = 'Помощь по командам.')

	emb.set_author( name = client.user.name, icon_url = client.user.avatar_url )
	emb.set_footer( text = 'Все права защищены by Кодик', icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )
	emb.set_thumbnail( url = 'https://vpochke.ru/wp-content/uploads/2017/04/help.jpg' )


	await ctx.send( embed = emb )

# мут
@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
async def mute(ctx, who: discord.Member, time: int, reason):
	emb = discord.Embed( title = 'Блокировка текстового каналов пользователю!', colour = discord.Colour.red() )
	emb.add_field( name = f'Произошла блокировка текстовых каналов пользователю:', value = f'{who}({who.mention})' )
	emb.add_field( name = 'Выдал наказание:', value = f'{ctx.author}({ctx.author.mention})' )
	emb.add_field( name = 'Время до снятия наказания:', value = f'{time} минут' )
	emb.add_field( name = 'По прчине:', value = '{}'.format(reason) )
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> мут пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`замутил в текстовых каналах!`**' )
	emb.add_field( name = '**Пользователя:**', value = f'{member.mention}' )
	emb.add_field( name = f'Причина:', value = '{}'.format(reason))
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757331969800667237)
	await channel.send(embed = emb)
	
	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'MUTE' )
	await who.add_roles(mute_role)
	await who.move_to(None)
	await asyncio.sleep(time * 60)
	await who.remove_roles(mute_role)

@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
async def unmute( ctx, who: discord.Member ):
	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'MUTE' )
	emb = discord.Embed( title = 'Разблокировка текстового канала', colour = discord.Colour.green() )
	emb.add_field( name = 'Была снята блокировка текстовых каналов пользователю:', value = f'{who}({who.mention})' )
	emb.add_field( name = 'Снял наказание модератор:', value = f'{ctx.author}({ctx.author.mention})' )
	await who.remove_roles(mute_role)
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> снятие мута с пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`снял мут!`**' )
	emb.add_field( name = '**С ользователя:**', value = f'{member.mention}' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757331969800667237)
	await channel.send(embed = emb)

@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
async def vmute(ctx, who: discord.Member, time: int, reason):
	emb = discord.Embed( title = 'Блокировка голосовых каналов пользователю!', colour = discord.Colour.red() )
	emb.add_field( name = f'Произошла блокировка голосовых каналов пользователю:', value = f'{who}({who.mention})' )
	emb.add_field( name = 'Выдал наказание:', value = f'{ctx.author}({ctx.author.mention})' )
	emb.add_field( name = 'Время до снятия наказания:', value = f'{time} минут' )
	emb.add_field( name = 'По прчине:', value = '{}'.format(reason) )
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> мут пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`замутил в голосовых каналах!`**' )
	emb.add_field( name = '**Пользователя:**', value = f'{member.mention}' )
	emb.add_field( name = f'Причина:', value = '{}'.format(reason))
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757331969800667237)
	await channel.send(embed = emb)

	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'VOICE MUTE' )
	await who.add_roles(mute_role)
	await who.move_to(None)
	await asyncio.sleep(time * 60)
	await who.remove_roles(mute_role)

@client.command(pass_context = True)
@commands.has_permissions(administrator = True)
async def vunmute( ctx, who: discord.Member ):
	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'VOICE MUTE' )
	emb = discord.Embed( title = 'Разблокировка голосовых каналов', colour = discord.Colour.green() )
	emb.add_field( name = 'Была снята блокировка голосовых каналов пользователю:', value = f'{who}({who.mention})' )
	emb.add_field( name = 'Снял наказание модератор:', value = f'{ctx.author}({ctx.author.mention})' )
	await who.remove_roles(mute_role)
	await ctx.send( embed = emb )

	emb = discord.Embed(title = '**Discord >> снял мут с пользователя пользователя!**')
	emb.add_field(name = f'**Администратор:**', value = f'{ctx.author.mention}' )
	emb.add_field( name = '**Действие:**', value = '**`снял мут с голосовых канало!`**' )
	emb.add_field( name = '**С пользователя:**', value = f'{member.mention}' )
	emb.set_footer( text = 'Techical support by Kodiknarkotik#0001', icon_url = 'https://thehackpost.com/wp-content/uploads/2019/11/Secret-Facts-Concerning-Identification-Technology-Disclosed-by-an-Expert.jpg' )
	channel = client.get_channel(757331969800667237)
	await channel.send(embed = emb)

@client.command(pass_context = True)
async def help( ctx, ):
	embed1 = discord.Embed( title = 'Помощь по командам сервера', description = '1 страница - ознакомление! \n 2 страница - Пользовательские команды! \n 3 страница - Команды доступные только Technical Administrator!', url = 'https://i.ytimg.com/vi/Rlt9UGpmz2I/maxresdefault.jpg' , colour = discord.Colour.blue() )
	embed2 = discord.Embed( title = 'Пользовательские команды', description = '/help - `Помощь по командам.` \n /avatar - `Посмотреть текущий аватар пользователя.` \n /info - `Информация о дискорд боте.`\n /cash	- `Посмотреть количество монет` \n /casino [Ставка] - `Сиграть в казино на ставку.` \n /pay [Пользователь#1234] [сумма] - `Передать указанному пользователю валюту`', colour = discord.Colour.green() )
	embed3 = discord.Embed( title = 'Administrator Commands', description = '/ban [@Провокатор#1234] [Причина] - `заблокировать участника` \n /unban [@Провокатор#1234] - `Разблокировать участника` \n /mute [@Провокатор#1234] [Время] [Причина] - `Заткнуть участника!` \n /kick [@Провокатор#1234] - `Выгнать участника.` \n /clear - `Очистка чата.` \n /amoney [@Пользователь#1234] [Сумма] - `Выдать пользователю валюту` \n /tmoney [@Провокатор#1234] [Сумма / all] - `Отнять у пользователя валюту / польностью обнулить счет`', colour = discord.Colour.red() )
	embeds = [embed1, embed2, embed3]
	message = await ctx.send( embed = embed1 )
	page = pag(client, message, only=ctx.author, use_more=False, embeds=embeds)
	await page.start()

@client.command()
async def avatar( ctx, member: discord.Member = None):
	if member is None:
		emb = discord.Embed(description=f'{ctx.author.mention}, Вот аватар пользователя { ctx.author.mention }', colour = discord.Colour.gold())
		emb.set_image( url = member.avatar_url )
		emb.set_footer( text = 'Все права защищены by Кодик')
		await ctx.send( embed = emb )
	else:
		emb = discord.Embed(description=f'{ctx.author.mention}, Вот аватар пользователя { member.mention }', colour = discord.Colour.gold())
		emb.set_image( url = member.avatar_url )
		emb.set_footer( text = 'Все права защищены by Кодик', icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )
		await ctx.send( embed = emb )

@client.command()
async def info( ctx ):
	emb = discord.Embed( title = '🔥Информация о дискорд боте!🔥', colour = discord.Colour.green() )
	emb.add_field( name = '🔞Разработчик бота:', value = '`Разработчиком данного бота является [Teh] Кодик#5062`' )
	emb.add_field( name = '✅Верификация:', value = '`Бот является верефицированным,официально подтвержденным.`' )
	emb.add_field( name = '🏥Уровень проверки:', value = '`Максимальный с подтверждением номера телефона`' )
	emb.add_field( name = ' Версия бота:', value = '`Version 0.1`' )
	emb.add_field( name = '☑Стадия разроботки:', value = '`Бот готов на 40%`' )
	emb.set_footer( text = 'Technical Suppot by [Teh] Kodi_Linderman' ,icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )
	emb.set_thumbnail( url = 'https://prowebber.ru/uploads/posts/2018-02/1518433579_ai-bots.png' )

	await ctx.send( embed = emb )

@client.command()
async def serverinfo( ctx ):
	emb = discord.Embed( title = '☪Информация о сервере "Linderman Family"☪', colour = discord.Colour.gold() )
	emb.add_field( name = 'Верефикация:', value = '`Сервер не является официальным или подтвержденным!`' )
	emb.add_field( name = '♕Владелец:', value = '<@!611397317580423180>' )
	emb.add_field( name = '✔Высшая роль:', value = '<@&714885361209442374>' )
	emb.add_field( name = '✘Роль агентов Тех.Поддержки:',value = '<@&735960298694901860>' )
	emb.add_field( name = '⌨Регион:', value = '`India`' )
	emb.add_field( name = '🏥Уровень проверки:', value = '`Максимальный с подтверждением номера телефона`' )
	emb.add_field( name = '☒Защита:', value = '`Установлена Тех.поддержкой`' )
	emb.set_footer( text = 'Technical Suppot by [Teh] Kodi_Linderman' ,icon_url = 'http://getwallpapers.com/wallpaper/full/b/3/0/1420610-hacker-background-2048x1400-for-ipad.jpg' )

	await ctx.send( embed = emb )

@client.command()
@commands.has_permissions( administrator = True )

async def teh(ctx):
	await ctx.channel.purge( limit = 1 )
	emb = discord.Embed( title = 'Раздел технической помощи! \n На серере "Linderman Family"', colour = discord.Colour.blue() )
	emb.add_field( name = 'Технический раздел:', value = '`В данном канале вы можете получить всю интересующую вас информацию о семье,дискорд сервере и т.п.`' )
	emb.add_field( name = 'Общее количество вопросов:', value = '`5`' )
	emb.add_field( name = 'Количество вопросов на расмотрении:', value = '`0`' )
	emb.add_field( name = 'Неотвеченых вопросов:', value = '`0`' )
	emb.set_thumbnail( url = 'https://st.depositphotos.com/1009659/1981/i/450/depositphotos_19816195-stock-photo-technical-support-and-tools-sign.jpg' )
	emb.set_image( url = 'https://nwlk.ru/images/new/prezent/tehpodderjka.png' )
	emb.set_footer( text = 'Technical Suppot Linderman Family | Кодик все права защищены', icon_url = 'http://st.depositphotos.com/1431107/1460/v/950/depositphotos_14605225-stock-illustration-support-vector-icon.jpg' )


	await ctx.send( embed = emb )



#Ошибки которые выдает бот

@clear.error
async def clear_error( ctx, error ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Команда не найдена!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У бота недостаточно прав!\n'
            f'❗ Если это не модераторская команда: то значит у бота нету права управлением сообщениями или права на установку реакций.', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, discord.Forbidden):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У вас недостаточно прав!', colour = discord.colour.gold()))
        elif isinstance(error, commands.BadArgument):
            if "Member" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пользователь не найден!', colour = discord.colour.gold()))
            if "Guild" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Сервер не найден!', colour = discord.colour.gold()))
            else:
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Введён неверный аргумент!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пропущен аргумент с названием {error.param.name}!', colour = discord.colour.gold()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Воу, Воу, Не надо так быстро прописывать команды.\n'
            f'❗ Подожди {error.retry_after:.2f} секунд и сможешь написать команду ещё раз.'))
        raise error

@unban.error
async def unban_error( ctx, error ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Команда не найдена!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У бота недостаточно прав!\n'
            f'❗ Если это не модераторская команда: то значит у бота нету права управлением сообщениями или права на установку реакций.', colour = 0xFB9E14))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, discord.Forbidden):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У вас недостаточно прав!', colour = discord.colour.gold()))
        elif isinstance(error, commands.BadArgument):
            if "Member" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пользователь не найден!', colour = discord.colour.gold()))
            if "Guild" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Сервер не найден!', colour = discord.colour.gold()))
            else:
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Введён неверный аргумент!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пропущен аргумент с названием {error.param.name}!', colour = discord.colour.gold()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Воу, Воу, Не надо так быстро прописывать команды.\n'
            f'❗ Подожди {error.retry_after:.2f} секунд и сможешь написать команду ещё раз.'))
        raise error

@kick.error
async def kick_error( ctx, error ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Команда не найдена!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У бота недостаточно прав!\n'
            f'❗ Если это не модераторская команда: то значит у бота нету права управлением сообщениями или права на установку реакций.', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, discord.Forbidden):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У вас недостаточно прав!', colour = discord.colour.gold()))
        elif isinstance(error, commands.BadArgument):
            if "Member" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пользователь не найден!', colour = discord.colour.gold()))
            if "Guild" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Сервер не найден!', colour = discord.colour.gold()))
            else:
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Введён неверный аргумент!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пропущен аргумент с названием {error.param.name}!', colour = discord.colour.gold()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Воу, Воу, Не надо так быстро прописывать команды.\n'
            f'❗ Подожди {error.retry_after:.2f} секунд и сможешь написать команду ещё раз.'))
        raise error

@mute.error
async def mute_error( ctx, error ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Команда не найдена!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У бота недостаточно прав!\n'
            f'❗ Если это не модераторская команда: то значит у бота нету права управлением сообщениями или права на установку реакций.', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, discord.Forbidden):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У вас недостаточно прав!', colour = discord.colour.gold()))
        elif isinstance(error, commands.BadArgument):
            if "Member" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пользователь не найден!', colour = discord.colour.gold()))
            if "Guild" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Сервер не найден!', colour = discord.colour.gold()))
            else:
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Введён неверный аргумент!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пропущен аргумент с названием {error.param.name}!', colour = discord.colour.gold()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Воу, Воу, Не надо так быстро прописывать команды.\n'
            f'❗ Подожди {error.retry_after:.2f} секунд и сможешь написать команду ещё раз.'))
        raise error

@ban.error
async def ban_error( ctx, error ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Команда не найдена!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У бота недостаточно прав!\n'
            f'❗ Если это не модераторская команда: то значит у бота нету права управлением сообщениями или права на установку реакций.', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, discord.Forbidden):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, У вас недостаточно прав!', colour = discord.colour.gold()))
        elif isinstance(error, commands.BadArgument):
            if "Member" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пользователь не найден!', colour = discord.colour.gold()))
            if "Guild" in str(error):
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Сервер не найден!', colour = discord.colour.gold()))
            else:
                return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Введён неверный аргумент!', colour = discord.colour.gold()))
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Пропущен аргумент с названием {error.param.name}!', colour = discord.colour.gold()))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=discord.Embed(description=f'❗ {ctx.author.name}, Воу, Воу, Не надо так быстро прописывать команды.\n'
            f'❗ Подожди {error.retry_after:.2f} секунд и сможешь написать команду ещё раз.'))
        raise error

@client.event
async def on_voice_state_update(member, before = None, after = None):
        if not member.guild.id == 734918408218477048:
            return

        if after.channel == None:
            return

        if (not before.channel == None) and (not after.channel == None):
            if before.channel.id == after.channel.id:
                return

        if not after.channel == None:
            if after.channel.id == 737276526675886130:
                mainCategory = discord.utils.get(member.guild.categories, id=737274644033306705
                	)
                ath = re.split(r'\W+', str(member))
                channel2 = await member.guild.create_voice_channel(name=f"Приватный канал {member.display_name} | {ath[-1]}", category=mainCategory)
                await channel2.set_permissions(member, view_channel = True, connect = True, manage_channels = False, manage_permissions = False, speak = False, move_members = False, use_voice_activation = True, priority_speaker = True, mute_members = False, deafen_members = False)
                vch = client.get_channel(737276526675886130)
                if not vch.members:
                    await channel2.delete()
                    return
                else:
                    if member in vch.members:
                        await member.move_to(channel2)
                        if not channel2.members:
                            await channel2.delete()
                            return
                    else:
                        await channel2.delete()
                        return 
                def check(a,b,c):
                    return len(channel2.members) == 0
                await client.wait_for('voice_state_update', check=check)
                await channel2.delete()

@client.command(pass_context = True)
async def padd(ctx, member: discord.Member):
	emb = discord.Embed(description = f'{ctx.author.mention}, вы добавили для пользователя {member.mention}, следущие права: \n --> Видеть ваш голосовой канал\n --> Подключатся к вашему голосовому каналу \n --> Говорить в вашем голосовом канале')
	await ctx.send( embed = emb )


@client.command(pass_context=True)
@commands.has_permissions(administrator = True)
async def arole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await ctx.message.add_reaction('✅')


#@client.command(pass_context=True)
#@commands.has_permissions( administrator = True )
#async def drole(ctx, user: discord.Member, role: discord.Role):
#    await user.remove_roles(role)
#    await ctx.channel.purge( limit = 1 )
#    emb = discord.Embed( description = f'{ user.mention }, **модератор** { ctx.author.mention } **снял с вас роль.** \n **`Роль`** { role.mention } **`была снята.`**', title = 'Ролевой БОТ', colour = discord.Colour.red() )
#    emb.set_footer( text = 'Technical Suppot | Кодик все права защищены', icon_url = 'http://st.depositphotos.com/1431107/1460/v/950/depositphotos_14605225-stock-illustration-support-vector-icon.jpg' )
#
#    await ctx.send( embed = emb )

@client.command(pass_context=True)
async def Роль( ctx, *, message: str ):
	channel = client.get_channel(748202589069377647)
	await channel.send(f'Пришел запрос на обработку от пользователя { author.mention }')

@client.command(pass_context = True)
@commands.check(is_owner)
async def Test(ctx):
	await ctx.send(f'**`[Try] Тест дак тест`**')
	await asyncio.sleep(1)
	await ctx.send('Кхм че за хуйня произошла?')

# МАФИЯ

global chisla
chisla = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']

@client.event
async def on_voice_state_update(member, before = None, after = None):
  global chisla
  if after.channel != None:

    if after.channel.id == 747892019933741198:
      if len(chisla) != 0:
        i = min(chisla)
        chisla.remove(i)
        await member.add_roles(discord.utils.get(member.guild.roles, id = 748200426675109890))
        return await member.edit(nick = i)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def mstart(ctx):
    emb = discord.Embed(title=f'Статистика по игре',
                        description= (f'**Ведущий >> {ctx.author.mention}** \n **Пользователи: ** \n **нажмите на ✅ для того чтобы присоединится!**'),
                        colour=discord.Color.purple())
    message = await ctx.send(embed=emb)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    await message.add_reaction('▶')
    await message.add_reaction('❔')
    
@client.command()
@commands.check(is_owner)
async def check(ctx):
	await ctx.send('[CHECK] Системная проверка текстового канала!', delete_after = 60)

@client.command()
@commands.has_permissions(administrator = True)
async def addrol(ctx):
    if ctx.guild.id == 727188568988188782:
        return await ctx.author.add_roles(discord.utuls.get(ctx.guild.roles, id = 727199250504745021))

token = ( 'NzM1MDczNjc4NjEzNjc2MDMz.Xxa8tQ.4KZQvgPBTyVXScOtp0QnZFjmyBc' )

client.run( token )    