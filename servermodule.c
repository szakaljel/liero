#include <Python.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <pthread.h>
#include "queque.h"
#include "message.h"

// jesli chcesz wiecej klietow zmiana stalej + zbudowanie 
// i wklejenie biblioteki ( python setup_server.py build )
// nowa wersja w katalogu build/...

#define CLIENT_SIZE 1
//moze trzeba bedzie napisac del queque i msg zwalniac



pthread_mutex_t mutex_send[CLIENT_SIZE];
pthread_mutex_t mutex_recv[CLIENT_SIZE];

pthread_t task[CLIENT_SIZE];

struct fifo * q_send[CLIENT_SIZE];
struct fifo * q_recv[CLIENT_SIZE];

int sockfd, newsockfd[CLIENT_SIZE], portno;
socklen_t clilen;
char buffer[CLIENT_SIZE][256];
struct sockaddr_in serv_addr, cli_addr;

int ident=1;

static PyObject *
server_send(PyObject *self, PyObject *args);


static PyObject *
server_recv(PyObject *self);

static PyObject *
server_init(PyObject *self,PyObject * args);

static PyObject *
server_close(PyObject *self);

static PyObject *ServerError;

static PyMethodDef ServerMethods[] = {
    {"send", server_send, METH_VARARGS,"test funkcji"},
    {"recv", server_recv, METH_VARARGS,"test funkcji"},
    {"init", server_init, METH_VARARGS,"test funkcji"},
    {"close", server_close, METH_VARARGS,"test funkcji"},
    {NULL, NULL, 0, NULL}        /* Wartownik */
};


void error(const char *msg)
{
   	PyErr_SetString(ServerError, msg);
}


void * real_time(void * ptr)
{
    int id=ptr;
    int n;
	void* msg=0;
    MSG * tmp;
	while(1)
	{

        pthread_mutex_lock(&mutex_send[id]);
        msg=fifo_pop(q_send[id]);
        pthread_mutex_unlock(&mutex_send[id]);
        while(msg!=0)
        {
            tmp=(MSG*)msg;//
            
            n = write(newsockfd[id],msg,sizeof(MSG));
            

            pthread_mutex_lock(&mutex_send[id]);
            msg=fifo_pop(q_send[id]);
            pthread_mutex_unlock(&mutex_send[id]);
        
        }

        n = read(newsockfd[id],buffer[id],sizeof(MSG));
        
        if(n>0)
        {
            tmp=(MSG*)malloc(sizeof(MSG));
            memcpy(tmp,buffer[id],sizeof(MSG));
            pthread_mutex_lock(&mutex_recv[id]);
            fifo_push(q_recv[id],(void*)tmp);
            pthread_mutex_unlock(&mutex_recv[id]);
        }
        
	}
	return NULL;

}



PyMODINIT_FUNC
initserver(void)
{
    PyObject *m;

    m = Py_InitModule("server", ServerMethods);

    ServerError = PyErr_NewException("server.error", NULL, NULL);
    Py_INCREF(ServerError);
    PyModule_AddObject(m, "error", ServerError);
}

static PyObject *
server_init(PyObject *self,PyObject * args)
{
    int i;
    char *port;
    
    struct timeval timeout;

    MSG *m;

    if (!PyArg_ParseTuple(args,"s",&port))
        return NULL;
    
    printf("%s \n",port);

    timeout.tv_sec=0;
    timeout.tv_usec=5;

    for(i=0;i<CLIENT_SIZE;i++)
    {
	   q_send[i]=fifo_init();
	   q_recv[i]=fifo_init();
    }

     sockfd = socket(AF_INET, SOCK_STREAM, 0);
     if (sockfd < 0) 
        error("ERROR opening socket");
     bzero((char *) &serv_addr, sizeof(serv_addr));
     portno = atoi(port);
     serv_addr.sin_family = AF_INET;
     serv_addr.sin_addr.s_addr = INADDR_ANY;
     serv_addr.sin_port = htons(portno);
     if (bind(sockfd, (struct sockaddr *) &serv_addr,
              sizeof(serv_addr)) < 0) 
              error("ERROR on binding");
     listen(sockfd,5);
     clilen = sizeof(cli_addr);

     for(i=0;i<CLIENT_SIZE;i++)
     {
        newsockfd[i] = accept(sockfd, 
                 (struct sockaddr *) &cli_addr, 
                 &clilen);
        if (newsockfd[i] < 0) 
          error("ERROR on accept");

        m=(MSG*)malloc(sizeof(MSG));
    //test timeoutow

        if (setsockopt (newsockfd[i], SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout,sizeof(timeout)) < 0)
            error("setsockopt failed\n");

        if (setsockopt (newsockfd[i], SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout,sizeof(timeout)) < 0)
            error("setsockopt failed\n");
    
        m->ident=ident;
        m->x=0;
        m->y=0;
        ident++;

        fifo_push(q_send[i],(void*)m);

        pthread_mutex_init(&mutex_send[i], NULL);
	    pthread_mutex_init(&mutex_recv[i], NULL);
    
        pthread_create( &task[i], NULL,real_time, i);
    }
    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject *
server_send(PyObject *self, PyObject *args)
{
    int komu;
    //niwiem czy nie powoduje wycieku ale raczej nie
    MSG *m=(MSG*)malloc(sizeof(MSG));

    if (!PyArg_ParseTuple(args, "(i(iii))",&komu,&(m->ident),&(m->x),&(m->y)))
        return NULL;
    
    if(komu>0&&komu<=CLIENT_SIZE)
    {
        komu--;
        pthread_mutex_lock(&mutex_send[komu]);
        fifo_push(q_send[komu],(void*)m);
        pthread_mutex_unlock(&mutex_send[komu]);
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
server_recv(PyObject *self)
{
    static int i=0;
    MSG* tmp;


    pthread_mutex_lock(&mutex_recv[i]);
    tmp=fifo_pop(q_recv[i]);
    pthread_mutex_unlock(&mutex_recv[i]);

    if(tmp==0)
    i=(i+1)%CLIENT_SIZE;

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
server_close(PyObject *self)
{
    int i;
	//pthread_exit(&task);
    for(i=0;i<CLIENT_SIZE;i++)
    {
	   pthread_mutex_destroy(&mutex_send[i]);
	   pthread_mutex_destroy(&mutex_recv[i]);

	   close(newsockfd[i]);
    }
    close(sockfd);

    Py_INCREF(Py_None);
    return Py_None;
}



