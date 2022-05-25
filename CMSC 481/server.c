//Gokul Natarajan
//CMSC 481
//05/19/22
//Programming Assignment 2

//Server.c

#include<stdio.h>
#include<string.h>	//strlen
#include<sys/socket.h>
#include<arpa/inet.h>	//inet_addr
#include<unistd.h>	//write

int main(int argc , char *argv[])
{
	int socket_desc , client_sock , c , read_size;
	struct sockaddr_in server , client;
	char client_message[1000];
	
	//Create socket
	//AF_INET is for ipv4
	//SOCK_STREAM is for TCP
	socket_desc = socket(AF_INET , SOCK_STREAM , 0);
	if (socket_desc < 0)
	{
		printf("Error creating socket");
	}
	printf("Socket created");
	
	//Prepare the sockaddr_in structure
	server.sin_family = AF_INET;
	server.sin_addr.s_addr = INADDR_ANY;
	server.sin_port = htons( 8000 );
	
	//Bind
	if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
	{
		return 1;
	}
	printf("bind done");

	//Server is listening
	listen(socket_desc , 3);
	puts("Server Started");
	c = sizeof(struct sockaddr_in);
	
	//accept connection from an incoming client
	client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c);
	if (client_sock < 0)
	{
		perror("accept failed");
		return 1;
	}
	printf("Connection accepted");
	
	//Receive a message from client
	while( (read_size = recv(client_sock , client_message , 1000 , 0)) > 0 )
	{
		//Send the message back to client
		char message[1000] = "Message Recieved";
		write(client_sock , message , strlen(message));
	}
	
	if(read_size == 0)
	{
		printf("Client disconnected");
		fflush(stdout);
	}
	else if(read_size == -1)
	{
		perror("Rec failed");
	}
	
	return 0;
}
