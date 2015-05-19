#include <stdio.h>
#include <stdlib.h>
#include "queque.h"


struct fifo * fifo_init()
{
	struct fifo * tmp;
	tmp=(struct fifo *)malloc(sizeof(struct fifo));
	tmp->first=0;
	tmp->last=0;
 	return tmp;	
}

void fifo_push(struct fifo * list,void* x)
{
	struct elem * tmp;
	
	if(list->first!=0)
	{
		tmp=(struct elem *)malloc(sizeof(struct elem));
		list->first->next=tmp;
		tmp->war=x;
		tmp->next=0;
		list->first=tmp;
	}
	else
	{
		tmp=(struct elem *)malloc(sizeof(struct elem));
		list->first=tmp;
		list->last=tmp;
		tmp->war=x;
		tmp->next=0;
	}
	
};

void* fifo_pop(struct fifo * list)
{
	void* x;
	if(list->last!=0)
	{
		struct elem * tmp;
		tmp=list->last;
		list->last=tmp->next;
		if(tmp==list->first)
		{
			list->first=0;
		}
		x=tmp->war;
		//free(tmp->war);
		free(tmp);
		return x;
	}
	return	0;
}


