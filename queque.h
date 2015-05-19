struct elem
{
	void* war;
	struct elem * next;
};

struct fifo
{
	struct elem * last;
	struct elem * first;
};

struct fifo * fifo_init();

void fifo_push(struct fifo * list,void* x);

void* fifo_pop(struct fifo * list);