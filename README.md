# Discord Printer bot 

It's a bot. It's for discord. Maybe it sends stuff to a printer.

Currently support the following slash_commands: 
| command      | description                                                                                                                                                                                                  |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| print_text   | Prints the message given by the text variable.  Emojis are currently not supported and will show weirdly                                                                                                     |
| print_image  | Prints the next picture/sticker the user sends in this channel. The user can abort this process by sending 'abort'  Message containing the image can be deleted afterwards (Same goes for the abort message) |
| check_status | Checks the readiness status of the printer                                                                                                                                                                   |

Road to Awesome:

- Have a cool Printer at Home 🤓
- Pull the Repository
- Have a .env file lying around
- Create a Docker Image
- Run the docker image