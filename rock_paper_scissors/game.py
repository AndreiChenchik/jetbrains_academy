import random

default_choices = "rock,paper,scissors"

user_name = input("Enter your name: ")
print(f"Hello, {user_name}")

user_choices = input()
if not user_choices:
    choices = default_choices.split(",")
else:
    choices = user_choices.split(",")

rules = dict([(move, (choices[choices.index(move)+1:]
                      + choices[:choices.index(move)]
                      )[:int((len(choices)-1)/2)]) for move in choices])

possible_game_choices = list(rules.keys())

print(f"Okay, let's start")

user_choice = input()

try:
    with open("rating.txt", "r") as file:
        data = file.readlines()
        scores = dict([(" ".join(line.split(" ")[:-1]),
                        int(line.split(" ")[-1])) for line in data])
except FileNotFoundError:
    scores = dict()

if user_name not in scores.keys():
    scores[user_name] = 0

while user_choice != "!exit":
    computer_choice = random.choice(possible_game_choices)

    if user_choice == "!rating":
        print(f"Your rating: {scores[user_name]}")
    elif user_choice not in possible_game_choices:
        print("Invalid input")
    elif user_choice == computer_choice:
        print(f"There is a draw ({user_choice})")
        scores[user_name] += 50
    elif computer_choice in rules[user_choice]:
        print(f"Sorry, but the computer chose {computer_choice}")
    else:
        print(f"Well done. The computer chose {computer_choice} and failed")
        scores[user_name] += 100
    user_choice = input()

with open("rating.txt", "w") as file:
    data = "\n".join([f"{score[0]} {score[1]}" for score in scores.items()])
    file.write(data)

print('Bye!')
