\# Interactive AI Agent Program

This project largely stems from my Prompt Engineering course's final project, which was to create an agent capable of executing distinct python commands (hence tools.py). I was also inspired last minute by Defunctlands video: "Disney's Living Characters: A Broken Promise". I wanted to make an interactive character application, one that would mimic my experience with LLM technology way back in the days of AIDungeon and Character.AI.

\## Challenges

Calling the API for text isn't all that hard.
Veo's Video is stuck to certain aspect rations, though i'd rather have a square.
Veo takes SO long to generate that the interactivity falls flat.

Canned Responses work better, but are not as interactive.

There's probably a way to make an AI model capable of posing an animation rig based on the text response, but thats a bit outside the scope of this project.



\## Design Patterns

* MVC Architecture

&nbsp;	Everything falls into its own file (including some outside the MVC like tools). Model.py handles calling each model. text requests are handled in chat, video requests are handled in generate\_veo\_video. View.py handles drawing the UI. Controller handles calling the model, using the selected character's prompt as a guideline. 

* Observer Pattern

&nbsp;	in Controller.py, we define chat\_finished and video\_ready as pyqtSignals, which grab the AI's responses once the model finishes.

* Worker Thread Pattern
  	Also in controller we use WorkerThread to ensure the app doesn't freeze while waiting for responses



\## OOP Pillars

* Encapsulation - each MVC class handles its own responsabilities and doesn't overstep.
* Abstraction - needs a bit of work here and there but each main loop calls a bunch of smaller defined functions to achieve the overall interaction.
* Inheritance - while we do inherit a bunch of stuff from existing python libraries, i dont really do any inheritance internally.
* Polymorphism - Again, we do override the QThread.run() method from an existing library, but we dont really override anything written for this project. 





\## AI Usage
AI was used extensively in the making of this project, primarily because i was not familiar with python, a requirement for another course.
a peculiar challenge in using AI for this is that its knowledge base is not up to date with the latest models, and struggles to implement them.

