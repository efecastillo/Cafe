# Coffee Club
#### Video Demo:  https://youtu.be/G4OTolIWu1U

#### Description:
The main goal is to keep track of coffee consumption among my colleagues.
I live in Chile so the website is in spanish.
Office coffee is **terrible**, so we have a system where different people bring their bags of coffee and we brew in french press for several members at the same time. Different bags of coffee have different price and every round of coffee involves different members, so it is laborious to keep track using just pen and paper.

The main framework is based of the Finance problem of week 9.
For the final deployment I will remove the option of registering to avoid bots but also trolls from the office, which sadly abound. I will register people manually. This is meant to have at most 20 users all of which working on the same place.

# User experience
As a registered user you have the following options available to you

## Add a bag of coffee
> This is bolsa.html
Say you buy a bag of coffee and want to share. You input the country of origin and some brand to remember it.
We also need to know the cost of the bag and how many grams of coffee.
These two numbers are instructed to be entered as *integers*. In the case of price this number will be usually in the thousands and grams below a thousand. To avoid dealing with formats of commas, dots, and floats, the web app rejects input that is not a whole positive number (there is also a check that the number is reasonable).
The result is kept in cafe.db

## Remove a bag of coffee
> This is a simple functionality from the main menu
If the bag is empty, there you have to mark it as gone.

## Register a coffee round
> This in in ronda.html
This is the most important part.
This is meant to be used from your cell phone while brewing the coffee (this explains the size of the images; huge on a large screen but they adapt to the device).
One need to input
1. The bag of coffee (menu will only show active bags, which is why finished bags have to be marked too)
2. The amount in mL begin brewed
3. The members drinking it
With this info the program can easily charge each member the right price.
There is also a small fee for me, the manager, on each cup.

Additionally, there was a functionality suggested by a member, because we are user-oriented:
4. Adding member's friends
If there is a colleague that is only here for one day, it would be silly to register the person for only one use.
Instead, a member can mark it as a guest for themselves and pay for them

## See the whole receipt
> This is factura.html
A member is owed by the coffee bags. 
And a member owes the cups that they drink.
The final balance is the main point, with all the details of consumption.
We discussed it with my colleagues and members receive nothing for contributing the french press.

## See all bags
> This is in bolsas.html
You can see what is availabe and also the finished bags. We keep track of the origin and brand so that people can remember and develop particular tastes.

## The homepage
The welcoming menu gives you an overview of the bags that you have active and your 5 most recent cups (with a link for the full receipt).

# Under the hood
We are using a SQLlite database whose schema is in the file
> schema.md
This was a good example of relational databases, as I thought at the beggining that a simple csv would suffice.
But having all the different items in their own table, plus the matchings in a different one, ended up in cleaner code.

We used bootstrap for css with some additionaly tweaks, but nothing fancy.
I felt the simple functionality called for a visually minimalistic approach.

The rest of the code is vanilla python in the files app.py and helpers.py.
Nothing outside of lecture 6 was required.
At several points, rather than me cleaning the input of the users, I simply reject inputs that are not in my preferred format.
For instance the code only uses integer numbers without any extra formatting.

I am aware of potentially malicious attacks, which is why I won't let strangers register.
As long as I know personally the people involved, I will ignore the validations issues that we saw in Lecture 8.
