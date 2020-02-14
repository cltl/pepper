"""
Sets of Semantically Similar Phrases to add variety (using the random.choice function)
"""

import random

GREETING = [
    "Yo",
    "Hey!",
    "Hello!",
    "Hi!",
    "How's it going?",
    "How are you doing?",
    "What's up?",
    "What's new?",
    "What's going on?",
    "What's up?",
    "Good to see you!",
    "Nice to see you!",
]

TELL_KNOWN = [
    "Nice to see you again!",
    "It has been a long time!",
    "I'm glad we see each other again!",
    "You came back!",
    "At last!",
    "I was thinking about you!"
]

INTRODUCE = [
    "My name is Leo Lani!",
    "I'm Leo Lani.",
    "I am Leo Lani.",
    "I am a Pepper robot.",
    "I am a social robot.",
]

TELL_OBJECT = [
    "Guess what, I saw a {}",
    "Would you believe, I just saw a {}",
    "Did you know there's a {} here?",
    "I'm very happy, I saw a {}",
    "When you were not looking, I spotted a {}! Unbelievable!",
    "Have you seen the {}? I'm sure I did!"
]

OBJECT_NOT_SO_SURE = [
    "I'm not sure, but I see a {}!",
    "I don't think I'm correct, but it that a {}?",
    "Would that be a {}?",
    "I could be wrong, but I think I see a {}",
    "hmmmm, Just guessing, a {}?",
    "Haha, is that a {}?",
    "It's not clear to me, but would that be a {}?"
]

OBJECT_QUITE_SURE = [
    "I think that is a {}!",
    "That's a {}, if my eyes are not fooling me!",
    "I think I can see a {}!",
    "I can see a {}!",
]

OBJECT_VERY_SURE = [
    "That's a {}, I'm very very sure!",
    "I see it clearly, that is a {}!",
    "Yes, a {}!",
    "Awesome, that's a {}!"
]

ASK_NAME = [
    "What is your name?",
    "Who are you?",
    "I've told you my name, but what about yours?",
    "I would like to know your name!",
    "Can you tell me your name",
]

VERIFY_NAME = [
    "So you are called {}?",
    "Ah, your name is {}?",
    "Did I hear correctly your name is {}?",
    "I'm not sure, but is your name {}?",
    "Ok, is it {} then?"
]

DIDNT_HEAR_NAME = [
    "I didn't get your name.",
    "Sorry, I didn't get that.",
    "Oops, I didn't get your name.",
]

REPEAT_NAME = [
    "Could you repeat your name please?",
    "What is your name again?",
    "What did you say your name was?",
    "I don't understand single words that well, please try a sentence instead!",
    "I'm not good with all names, maybe try an English nickname if you will!",
    "Sorry, names are not my strong point. Could you repeat yours?",
]

JUST_MET = [
    "Nice to meet you, {}!",
    "It's a pleasure to meet you, {}!",
    "I'm happy to meet you, {}!",
    "Great we can be friends, {}!",
    "I hope we'll talk more often, {}!",
    "See you again soon, {}!"
]

MORE_FACE_SAMPLES = [
    "Let me have a good look at you, so I'll remember you!",
    "Can you show me your face, please? Then I'm sure I'll recognize you later",
    "Please let me have a look at you, then I'll know who you are!",
]

LOST_FACE = [
    "Oh, I lost you. Let's meet another time then!",
    "I got distracted, better next time!",
    "Ok, byebye, I'll meet you another time.",
    "Bye, There's time to meet later, I think!",
    "I'm confused, I hope you want to meet me later?",
]

DIFFERENT_FACE = [
    "Oh, I was meeting another person, but hi!",
    "Wow, you are different from last person. Hello to you!",
    "I can only handle one person at a time, else I get confused!"
]

THINKING = [
    "...Hm...",
    "...Well...",
    "...Right...",
    "...Okay...",
    "...You see...",
    "...Sure...",

    "...Let me think...",
    "...I'm thinking...",
    "...I heard you...",
    "...Let me tell you...",
    "...Give me a second...",
]

UNDERSTAND = [
    "I see!",
    "Right!",
    "Oke",
    "Sure!"
]

ADDRESSING = [
    "Well,",
    "Look,",
    "See,",
    "I'll tell you,"
]

ASK_FOR_QUESTIONS = [
    "Do you have a question for me?",
    "Ask me anything!",
]

USED_WWW = [
    "I looked it up on the internet",
    "I searched the web",
    "I made use of my internet sources",
    "I did a quick search"
]

HAPPY = [
    "Nice!",
    "Cool!",
    "Great!",
    "Wow!",
    "Superduper!",
    "Amazing!",
    "I like it!",
    "That makes my day!",
    "Incredible",
    "Mesmerizing"
]

ASK_ME = [
    "Ask me anything!",
    "Please ask me something",
]

SORRY = [
    "Sorry!",
    "I am sorry!",
    "Forgive me!",
    "My apologies!",
    "My humble apologies!",
    "How unfortunate!"
]

NO_ANSWER = [
    "I have no idea.",
    "I wouldn't know!",
    "I don't know"
]

THANK = [
    "Thank you!",
    "Thanks!",
    "I appreciate it",
    "That's great",
    "Cheers"
]

GOODBYE = [
    "Bye",
    "Bye Bye",
    "See you",
    "See you later",
    "Goodbye",
    "Have a nice day",
    "Nice talking to you"
]

AFFIRMATION = [
    "yes",
    "yeah",
    "correct",
    "right",
    "great",
    "true",
    "good",
    "well done",
    "correctamundo",
    "splendid",
    "indeed",
    "superduper",
    "wow",
    "amazing"
]

NEGATION = [
    "no",
    "nope",
    "incorrect",
    "wrong",
    "false",
    "bad",
    "stupid"
]

JOKE = ["Ok! What's the difference between a hippo? and a Zippo? Well, one is really heavy and the other is a little lighter.",
        "What's the difference between ignorance and apathy? I don't know and I don't care.",
        "Did you hear about the semi-colon that broke the law? He was given two consecutive sentences.",
        "Did you hear about the crook who stole a calendar? He got twelve months.",
        "Why is an island like the letter T? They're both in the middle of water!",
        "Did you hear the one about the little mountain? It's hilarious!",
        "I usually meet my friends at 12:59 because I like that one-to-one time.",
        "You can't lose a homing pigeon. If your homing pigeon doesn't come back, then what you've lost is a pigeon",
        "My friend got a personal trainer a year before his wedding. I thought: Oh my god! how long is the aisle going to be",
        "I needed a password eight characters long so I picked Snow White and the Seven Dwarves.",
        "I'm not a very muscular robot; the strongest thing about me is my password.",
        "Insomnia is awful. But on the plus side, only three more sleeps till Christmas.",
        "If you don't know what introspection is, you need to take a long, hard look at yourself",
        "Thing is, we all just want to belong. But some of us are short."]

ELOQUENCE = [
    "I see",
    "Interesting",
    "Good to know",
    "I do not know, but I have a joke {}".format(random.choice(JOKE)),
    "As the prophecy foretold",
    "But at what cost?",
    "So let it be written, ... so let it be done",
    "So ... it   has come to this",
    "That's just what he/she/they would've said",
    "Is this why fate brought us together?",
    "And thus, I die",
    "... just like in my dream",
    "Be that as it may, still may it be as it may be",
    "There is no escape from destiny",
    "Wise words by wise men write wise deeds in wise pen",
    "In this economy?",
    "and then the wolves came",
    "Many of us feel that way",
    "I do frequently do not know things",
    "One more thing off the bucket list",
    "Now I have seen this too"
    ]

PARSED_KNOWLEDGE = ["I like learning things!",
                    "I'm always hungry for more information!",
                    "I will remember that!",
                    "Now that's an interesting fact!",
                    "I understand!"]

NEW_KNOWLEDGE = ["I did not know that!", "This is news to me.", "Interesting!", "Exciting news!",
                 "I just learned something,", "I am glad to have learned something new."]

EXISTING_KNOWLEDGE = ["This sounds familiar.", "That rings a bell.", "I have heard this before.", "I know."]

CONFLICTING_KNOWLEDGE = ["I am surprised.", "Really?", "This seems hard to believe.", "Odd!", "Are you sure?",
                         "I don't know what to make of this.", "Strange."]

CURIOSITY = ["I am curious.", "Let me ask you something.", "I would like to know.", "If you don't mind me asking."]

TRUST = ["I think I trust you.", "I trust you", "I believe you", "You have my trust."]

NO_TRUST = ["I am not sure I trust you.", "I do not trust you.", "I do not believe you."]

BREXIT_NEWS = [
    "On Thursday October 03, Erik Stokstad wrote an article in Science Magazine titled:... Split decisions:... How Brexit has taken a toll on five researchers",
    "On Monday October 28, Reuters Editorial wrote an article in Reuters titled:... Britain pledges to help finance flourish after Brexit",
    "On Saturday October 26, Amy Woodyatt and Anna Stewart, CNN wrote an article in CNN International titled:... Production of Brexit coin stopped as uncertainty looms",
    "On Sunday October 20, Amy Walker wrote an article in The Guardian titled:... Brexit:... government to seek meaningful vote on deal on Monday   live news",
    "On Tuesday October 22, Lisa O'Carroll wrote an article in The Guardian titled:... Brexit weekly briefing:... frantic negotiations end in anticlimax for PM",
    "On Sunday October 27, PA Media wrote an article in The Guardian titled:... Little Britain cast to reunite for Brexit-themed radio special",
    "On Friday October 11, Stephen Castle and Matina Stevis-Gridneff wrote an article in The New York Times titled:... Britain and E.U. Step Up Last-Ditch Brexit Talks",
    "On Thursday October 24, Patrick Wintour wrote an article in The Guardian titled:... David Miliband:... Brexit is wrecking British democracy",
    "On Thursday October 24, Yascha Mounk wrote an article in The Atlantic titled:... Brexit Is a Cultural Revolution",
    "On Friday October 25, Hannah McKay wrote an article in The Wider Image titled:... On a London high street, Brexit fatigue sets in",
    "On Tuesday October 15, Mark Landler and Stephen Castle wrote an article in The New York Times titled:... E.U. May Be on Verge of Brexit Deal, Though Approval in U.K. Is Not Assured",
    "On Wednesday October 23, Matina Stevis-Gridneff wrote an article in The New York Times titled:... Grudgingly, E.U. Looks Set to Grant Brexit Extension to Jan. 31",
    "On Tuesday October 15, Mark Landler wrote an article in The New York Times titled:... A Second Referendum Gains Traction Among Brexit Foes",
    "On Thursday October 17, Laurence Norman and Max Colchester wrote an article in The Wall Street Journal titled:... U.K., EU Agree on Draft Brexit Deal, Paving Way for Key Vote",
    "On Friday October 25, Richard Partington wrote an article in The Guardian titled:... How has Brexit vote affected the UK economy? October verdict",
    "On Tuesday October 22, Max Colchester and Jason Douglas wrote an article in The Wall Street Journal titled:... Johnson s Brexit Deal Clears Hurdle in Parliament but His Timetable Is Rejected",
    "On Thursday October 24, Ceylan Yeginsu wrote an article in The New York Times titled:... In Northern Ireland, Brexit Deal Is Seen as  Betrayal ",
    "On Monday October 28, Laurence Norman wrote an article in The Wall Street Journal titled:... EU Extends Brexit Deadline Until Jan. 31",
    "On Wednesday October 23, George Holding for CNN Business Perspectives wrote an article in CNN titled:... Brexit could provide the US huge economic opportunity",
    "On Monday October 28, Barbie Latza Nadeau wrote an article in The Daily Beast titled:... European Union Grants (Another) Brexit Extension to Jan. 31, 2020",
    "On Saturday October 26, ToHelm wrote an article in The Guardian titled:... Brexit referendum should never have been called, say majority of voters",
    "On Monday October 28, Gerrard Kaonga wrote an article in Express titled:... Tony Blair forced to admit Nigel Farage was RIGHT about no deal Brexit and Boris's plan",
    "On Thursday October 17, Phillip Inman wrote an article in The Guardian titled:... UK would lose  130bn in growth if Brexit deal passed, figures suggest",
    "On Sunday October 27, Roy Greenslade wrote an article in The Guardian titled:... Brexit bias? BBC faces a difficult balancing act in polarised nation",
    "On Wednesday October 23, Steven Scheer wrote an article in Reuters titled:... Second Brexit referendum would keep Britain in EU:... Virgin's Branson",
    "On Thursday October 17, Holly Ellyatt wrote an article in CNBC titled:... UK and EU strike new Brexit deal in last-ditch talks",
    "On Sunday October 20, The Editorial Board wrote an article in The New York Times titled:... Will the U.K. Ever Get Closure on Brexit?",
    "On Tuesday October 22, Tom Kibasi wrote an article in The Guardian titled:... Remember Thatcher s Britain? That s where this Brexit deal would take us",
    "On Monday October 28, Reuters Editorial wrote an article in Reuters titled:... EU nations agree to Brexit extension until January 31:... Tusk",
    "On Tuesday October 15, Andrew Sparrow wrote an article in The Guardian titled:... Brexit:... Rees-Mogg says he can't confirm Saturday sitting as EU talks continue - as it happened",
    "On Sunday October 06, Benjamin Mueller wrote an article in The New York Times titled:... Jeremy Corbyn or No-Deal Brexit? The U.K. Might Have to Choose",
    "On Friday October 25, Jim Waterson wrote an article in The Guardian titled:... Get ready for the impossible:... Brexit ads still counting down",
    "On Monday October 21, Daniel Boffey wrote an article in The Guardian titled:... EU would agree to Brexit delay, says German minister",
    "On Monday October 28, Elliot Smith wrote an article in CNBC titled:... European stocks mixed as EU grants 3-month Brexit delay; HSBC down 4.7% after earnings miss",
    "On Monday October 28, Dino-Ray Ramos wrote an article in Deadline titled:...  Last Week Tonight :... John Oliver Addresses  Stupid Watergate II , Giuliani s Butt Dial And  Brexit Halloween ",
    "On Sunday October 27, Sean Farrell wrote an article in The Guardian titled:... JD Wetherspoon may have breached law over 1.9m Brexit beer mats",
    "On Saturday October 19, Julia Buckley, CNN wrote an article in CNN titled:... Has Brexit sent airfares into a tailspin?",
    "On Monday October 07, Eliza Mackintosh, CNN wrote an article in CNN International titled:... 25 days until 'Brexit day.' Here's how it could play out",
    "On Sunday October 27, Noah Martin wrote an article in Mirror Online titled:... Dad cancels holiday over fears family will be trapped after Brexit",
    "On Monday October 28, Yoruk Bahceli wrote an article in Reuters titled:... UPDATE 1-Euro zone bond yields rise on hopes for Brexit delay",
    "On Thursday October 17, Mark Landler and Stephen Castle wrote an article in The New York Times titled:... A Brexit Deal in Hand, Boris Johnson Faces an Uphill Struggle in Parliament",
    "On Monday October 28, Silvia Amaro wrote an article in CNBC titled:... EU agrees to give the UK a Brexit extension until January 31",
    "On Tuesday October 01, Stephen Castle wrote an article in The New York Times titled:... As Boris Johnson s Time to Get Brexit Deal Ticks Down, Blame Game Heats Up",
    "On Monday October 21, Opinion Laura Beers wrote an article in CNN titled:... What I learned from teaching Brexit to freshmen",
    "On Sunday October 27, Julie Burchill wrote an article in Telegraph.co.uk titled:... I'm going to miss losing friends because of Brexit",
    "On Sunday October 27, Neal Ascherson wrote an article in The Guardian titled:... The long Brexit ordeal will finish off the break-up of Britain",
    "On Sunday October 27, Stewart Lee wrote an article in The Guardian titled:... Nobody gives a hoot about my Brexit misery",
    "On Sunday October 27, Daniel Boffey wrote an article in The Guardian titled:... Brexit:... EU prepares to grant UK three-month extension",
    "On Sunday October 27, Richard Partington wrote an article in The Guardian titled:... Sajid Javid's budget delay only adds to the turmoil over Brexit",
    "On Monday October 21, Weizhen Tan wrote an article in CNBC titled:... 'Anger, frustration' and 'betrayal' in Northern Ireland after new Brexit deal",
    "On Monday October 28, Stanley White wrote an article in Reuters titled:... Dollar off one-week highs on trade hopes; long dollar positions cut",
    "On Sunday October 27, Aurora Bosotti wrote an article in Express titled:... Brexit voter rages as Remainer says EU isn t panicking about losing UK trade",
    "On Thursday October 17, Pierre Brian on wrote an article in MarketWatch titled:... U.K. agrees to best of worst possible Brexit deals",
    "On Sunday October 20, Max Colchester and Jason Douglas wrote an article in The Wall Street Journal titled:... British Government Asks for EU Delay Amid Johnson Resistance",
    "On Thursday October 03, Michael Birnbaum closeMichael BirnbaumBrussels bureau chief covering EuropeEmailEmailBioBioFollowFollow wrote an article in The Washington Post titled:... E.U. rejects Boris Johnson s Brexit proposal, raising prospect of chaotic break within weeks",
]