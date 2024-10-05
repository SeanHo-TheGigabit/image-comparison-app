User usage flow will be:
1. Open the program, and it can set the video capture size and which capture stream, and also able to select the draw factor that will plot on the screen.
2. Once configure, user will be able to press "Operate" to start the video capturing and drawing.
3. Then user able to press a button "Save Sample" to screenshot down the image from the stream and save in the folder and update the image galery list for user to see.
4. User then can from the image gallery list to select which picture as the base for the comparison, once confirm press "Set to Compare"
5. If compare and get similar, will call to a function event_similar()
6. if it is not similar, will call to a function event_not_similar()
7. function event_similar() will print out the message
8. function event_not_similar() will print out the message

Apply design architecture to make the program robust to swap the image comparison function in future