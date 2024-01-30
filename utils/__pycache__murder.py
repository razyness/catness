import os
import shutil

"""
kill people with hammers
kill people with hammers
kill people with hammers

stop using hammers to nail stuff into walls, that's not what they're for
hi, my name is franklin hammer. 
in 2014, i had an idea: i should kill people
so to help me, i invented this bad boy.
it's for killing people, not for nail stuff.
what is this? this is nothing

have you ever killed anybody? It's AWESOME.
i've killed 1000 people.
it feels like HEROIN. you ever done heroin?
it's great, kinda just makes you feel, you know, nice.
so if you haven't done heroin, do heroin, and then kill a person with a hammer.
you'll be like 'whoa, that's like the same thing!'

and if i see you using a hammer for anything other than killing, guess what i'm going to do. 
and i can't get in trouble for it cause i got one of theese!
government gives you one of these when you make your first kill-y!
you can kill as many people as you want, you can be standing over a body with a bloody hammer, and a cop could see you, and you can show them this and he'll just be like "oop, alright."

so do heroin and kill somebody with a hammer this weekend!
"""


def delete_pycache(dir_path):
	for root, dirs, _ in os.walk(dir_path):
		if "__pycache__" in dirs:
			pycache_dir = os.path.join(root, "__pycache__")
			print(f"Deleting {pycache_dir}")
			shutil.rmtree(pycache_dir)


if __name__ == "__main__":
	dir_path = "."
	delete_pycache(dir_path)
