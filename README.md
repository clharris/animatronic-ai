### AI Animatronic

--------------------

This project is for creating an animatronic talking head that you can chat with and it will respond with AI-generated 
responses. My use-case was for a talking skull for Halloween (see the video [here](https://www.youtube.com/shorts/2F_gNuV8I8Y)).

There are is a hardware component and a coding component. This repo is for the programming component and pieces together
the four required parts:

- Recording speech - this requires listening in a loop and detecting when the speaker has stopped speaking
- Speech to text - this send the recorded wav file to the [Open AI Speech to Text API](https://platform.openai.com/docs/guides/speech-to-text)
- AI-generated response - this sends the text to an OpenAI GPT-4o model to get a response
- Text to speech - this uses [Piper]( https://github.com/rhasspy/piper) to use a voice model to return spoken text

Currently, there is quite a bit of latency and this will require optimizations or possibly a different model for a faster
response. I'll probably provide an update on that soon.

For the hardware component you'll need:

- Your animatronic - in my case a skull (the more "clickety clack" the jaw is, the better)
- A servo - I used [this one](https://www.amazon.com/dp/B003T6XGNU)
- Something to control it - I used a [raspberry pi 5](https://www.amazon.com/dp/B0D95QBKJ4) (you don't necessarily need the full kit)
- Parts to connect the servo to the jaw - like [this](https://www.amazon.com/dp/B0006O4G7S), [this](https://www.amazon.com/dp/B0006O4GFK), and [this](https://www.amazon.com/dp/B0006O4G4Q)
- For a raspberry pi you may get a lot of "jitters" from the servo - I used [this](https://www.amazon.com/dp/B01D1D0CX2) to help with that (powered by [this](https://www.amazon.com/dp/B08JYPMCZY)). [Here](https://www.youtube.com/watch?v=oeLmbXrHi_c&t=192s) is a good YouTube video explaining more on this.

Here are a couple fo good YouTube videos for helping with the hardware setup
- https://youtu.be/Jk3ZsyrTU4M?si=O4LXjLbh5Ey28FjZ&t=238
- https://youtu.be/DB4wycBrt8g?si=hl8YFrcRGmIeZ64t&t=266



