#include <Python.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <pthread.h>
#include "queque.h"
#include "message.h"



pthread_mutex_t mutex_send;
pthread_mutex_t mutex_recv;

pthread_t task;

struct fifo * q_send=0;
struct fifo * q_recv=0;

int sockfd, portno, n;
struct sockaddr_in serv_addr;
struct hostent *server;

char buffer[256];


static PyObject *
client_send(PyObject *self, PyObject *args);

static PyObject *
client_recv(PyObject *self);

static PyObject *
client_init(PyObject *self,PyObject *args);

static PyObject *
client_close(PyObject *self);

static PyObject *ClientError;

static PyMethodDef ClientMethods[] = {
    {"send", client_send, METH_VARARGS,"test funkcji"},
    {"recv", client_recv, METH_VARARGS,"test funkcji"},
    {"init", client_init, METH_VARARGS,"test funkcji"},
    {"close", client_close, METH_VARARGS,"test funkcji"},
    {NULL, NULL, 0, NULL}        /* Wartownik */
};


void error(const char *msg)
{
   	PyErr_SetString(ClientError, msg);
}


void * real_time(void * ptr)
{
	void* msg=0;
    MSG * tmp;
	while(1)
	{
		pthread_mutex_lock(&mutex_send);
    	msg=fifo_pop(q_send);
    	pthread_mutex_unlock(&mutex_send);
		while(msg!=0)
		{
            tmp=(MSG*)msg;
            
			n = write(sockfd,msg,sizeof(MSG));

			pthread_mutex_lock(&mutex_send);
    		msg=fifo_pop(q_send);
    		pthread_mutex_unlock(&mutex_send);
    	
		}

        n = read(sockfd,buffer,sizeof(MSG));
       
        if(n>0)
        {
            tmp=(MSG*)malloc(sizeof(MSG));
            memcpy(tmp,buffer,sizeof(MSG));
            pthread_mutex_lock(&mutex_recv);
            fifo_push(q_recv,(void*)tmp);
            pthread_mutex_unlock(&mutex_recv);
        }
		
	}
	return NULL;

}



PyMODINIT_FUNC
initclient(void)
{
    PyObject *m;

    m = Py_InitModule("client", ClientMethods);

    ClientError = PyErr_NewException("client.error", NULL, NULL);
    Py_INCREF(ClientError);
    PyModule_AddObject(m, "error", ClientError);
}

static PyObject *
client_init(PyObject *self,PyObject *args)
{
    int i = 1;

    struct timeval timeout;

    char *port;
    char *ip;
    if (!PyArg_ParseTuple(args,"(ss)",&port,&ip))
        return NULL;

    timeout.tv_sec=0;
    timeout.tv_usec=5;

    printf("%s %s \n",port,ip);

	q_send=fifo_init();
	q_recv=fifo_init();


    portno = atoi(port);
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");
    server = gethostbyname(ip);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }
    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
         (char *)&serv_addr.sin_addr.s_addr,
         server->h_length);
    serv_addr.sin_port = htons(portno);
    if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
        error("ERROR connecting");


    //test timeoutow

    
    if(setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, (void *)&i, sizeof(i)))
        error("setsockopt failed\n");

    if (setsockopt (sockfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout,sizeof(timeout)) < 0)
        error("setsockopt failed\n");

    if (setsockopt (sockfd, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout,sizeof(timeout)) < 0)
        error("setsockopt failed\n");
    

    pthread_mutex_init(&mutex_send, NULL);
	pthread_mutex_init(&mutex_recv, NULL);
    
    pthread_create( &task, NULL,real_time, NULL);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
client_send(PyObject *self, PyObject *args)
{
  
    MSG *m=(MSG*)malloc(sizeof(MSG));

    if (!PyArg_ParseTuple(args, "(iii)",&(m->ident),&(m->x),&(m->y)))
        return NULL;
    
    pthread_mutex_lock(&mutex_send);
    fifo_push(q_send,(void*)m);
    pthread_mutex_unlock(&mutex_send);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
client_recv(PyObject *self)
{
    MSG* tmp;

    pthread_mutex_lock(&mutex_recv);
    tmp=fifo_pop(q_recv);
    pthread_mutex_unlock(&mutex_recv);

    if(tmp==0)
    {
        Py_INCREF(Py_None);
        return Py_None;   
    }
    else
    {
        return Py_BuildValue("(iii)",tmp->ident,tmp->x,tmp->y);
    }

    
}

static PyObject *
client_close(PyObject *self)
{
	
	pthread_mutex_destroy(&mutex_send);
	pthread_mutex_destroy(&mutex_recv);

	close(sockfd);

    Py_INCREF(Py_None);
    return Py_None;
}



