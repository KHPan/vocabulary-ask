#quizlet2的python版
import os
import glob
import time
import random
random.seed(time.time())
import copy
# import webbrowser
import datetime
import json
import traceback

class InstructionException(Exception):
	pass

class CheckContentException(Exception):
	pass

def checkContent(words):
	if not isinstance(words, list):
		raise CheckContentException("檔案應是一個list")
	for word in words:
		if not isinstance(word, list):
			raise CheckContentException(f"{word}的應是一個list")
		if len(word) not in (2, 3):
			raise CheckContentException(f"{word}的長度不合法")
		for w in word:
			if not isinstance(w, str):
				raise CheckContentException(f"在{word}的{w}應是一個str")

red = "\033[91m"
green = "\033[92m"
blue = "\033[94m"
default = "\033[0m"

key_name = {"a": 0, "q": 1, "c": 2}
last_word = ""
seg = "\\d"
instructions = ("\\d", "\\e", "\\r", "\\f")
is_wrong = True
os.chdir(os.path.dirname(__file__))
while seg != "\\e":
	if seg == "\\d":
		if os.path.exists("_resume_.json"):
			filename = "_resume_.json"
			attrs = [filename]
			seg = "\\f"
			continue
		files = sorted(glob.glob('*.txt') + glob.glob('*.json'),
				 			key=os.path.getmtime)
		for index, filename in enumerate(files):
			print(f"{index}：{filename}")
		try:
			attrs = [ele.replace("\\s", " ") for ele in input("輸入檔案編號：").split(" ")]
			filename = files[int(attrs[0])]
		except KeyboardInterrupt:
			break
		except:
			print("輸入不合法")
			continue
		else:
			seg = "\\f"

	elif seg == "\\f":
		if filename is None:
			seg = "\\r"
			continue
		with open(filename, "r", encoding='utf-8') as file:
			if filename.endswith(".json"):
				words = json.load(file)
			elif filename.endswith(".txt"):		
				words = [ele.split("\t") for ele in file.read().split("\n") if ele != ""]
			try:
				checkContent(words)
			except CheckContentException as err:
				print(f"{err}")
				input("檔案內容有錯誤，請修改，按任意鍵重試...")
				continue
			except Exception as err:
				print("檔案有未知錯誤:")
				traceback.print_exc()
				input("檔案內容有錯誤，請修改，按任意鍵重試...")
				continue
		if filename == "_resume_.json":
			os.remove(filename)
			filename = None
		for attr in attrs[1:]:
			if attr.startswith("remove:"):
				to_be_removed = attr[len("remove:"):]
				words = [word for word in words if to_be_removed not in word[0]]
			elif attr.find("=") != -1:
				split = attr.split("=")
				try:
					to_be = key_name[split[0]]
				except KeyError:
					print(f"指令{attr}中只應授予a、q、c中的一個")
					continue
				try:
					to_get = [key_name[s.lower()] for s in split[1].split("+")]
				except KeyError:
					print(f"指令{attr}中只應來自a、q、c中的一個或多個並以加號串聯")
					continue
				for s in split[1].split("+"):
					if s.isupper():
						words = [word for word in words
			   				if len(word) > key_name[s.lower()]
								and word[key_name[s.lower()]] != ""]
				if len(words) == 0:
					print(f"指令{attr}中沒有符合條件的詞彙")
					continue
				for word in words:
					word[to_be] = sum((word[i] for i in to_get if i < len(word)), "")
			elif attr.find("/") != -1:
				try:
					keys = [key_name[s.lower()] for s in attr.split("/")]
				except KeyError:
					print(f"指令{attr}中只應來自a、q、c中的兩個或多個並以斜線串聯")
					continue
				new_words = []
				for word in words:
					for a, b in zip(keys[:-1], keys[1:]):
						if len(word) <= max(a, b) or word[a] == "" or word[b] == "":
							break
						word[a], word[b] = word[b], word[a]
					else:
						new_words.append(word)
				if len(new_words) == 0:
					print(f"指令{attr}中沒有符合條件的詞彙")
					continue
				words = new_words
			elif attr.find(":") != -1:
				split = attr.split(":")
				try:
					start = int(split[0])
				except ValueError:
					start = 0
				try:
					end = int(split[1])
				except ValueError:
					end = len(words)
				words = words[start:end]
			else:
				words = random.sample(words, int(attrs[1]))
		for index, word in enumerate(words):
			print(f"({index}/{len(words)})")
			print(word[1])
			print(word[0])
			if len(word) >= 3:
				if word[2] != "":
					print(word[2])
		seg = "\\r"

	elif seg == "\\r":
		que = copy.copy(words)
		try: 
			while len(que) > 0:
				wrong = []
				random.shuffle(que)
				for index, word in enumerate(que):
					if is_wrong:
						print(f"({blue}{len(que)-index}{default}, {red}{len(wrong)}{default}, {green}{index-len(wrong)}{default})")
					else:
						print(f"({blue}{len(que)-index}{default}")
					print(word[1])
					while True:
						while True:
							try:
								inp = input()
							except KeyboardInterrupt as err:
								with open("_resume_.json", "w", encoding='utf-8') as file:
									json.dump(que[index:] + wrong, file, ensure_ascii=False, indent=4)
								raise err
							if inp == "\\w":
								is_wrong = not is_wrong
							# elif inp == "\\v":
							# 	if last_word != "":
							# 		webbrowser.open(f"https://yue.forvo.com/word/{last_word}/")
							elif inp == "\\s":
								save_content = que[index:] + wrong
								with open(".".join(filename.split(".")[:-1]) + f"-擷取{len(save_content)}題" + 
													f"-{datetime.datetime.now().strftime('%Y%m%d%H%M')}.json",
													"w", encoding='utf-8') as file:
									json.dump(save_content, file, ensure_ascii=False, indent=4)
							else:
								break
						last_word = word[0]
						if set(inp.split('/')) == set(word[0].split('/')):
							break
						if len(wrong) == 0 or wrong[-1] != word:
							wrong.append(word)
						if inp in instructions:
							seg = inp
							raise InstructionException()
						print(word[0])
					if len(word) >= 3:
						if word[2] != "":
							print(word[2])
				que = wrong
				if len(wrong) > 0:
					input(f"錯了{len(wrong)}題，請按enter繼續...")
		except InstructionException:
			pass
		else:
			seg = input("測驗結束")
			while seg not in instructions:
				print("輸入合法指令")
				seg = input("測驗結束")