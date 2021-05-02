#include <stdio.h>
#include <stdlib.h>
#include "lwp.h"

typedef struct lwpNode
{
    int lwpPid;
    struct lwpNode *next;
} lwpNode;

void resetTail();
void lwpAdd(int pid);
void lwpDelete(int pid);
int rrScheduling();
lwp_context *getScheduledLWP();

/* Linked list of lwp's.*/
lwpNode *lwpHead;
lwpNode *lwpCur;

schedfun *scheduler;
/* Will hold all lwp created*/
lwp_context processTable[LWP_PROC_LIMIT];
/* Keeps track of lwp PID and idx.*/
unsigned long lwpCount = 0;
/* Keeps track of curLWP*/
lwp_context *curLwp;
/* Holds original stack pointer.*/
ptr_int_t *pStack;
int lwp_running = 0;
int offset = 1;

/* Function that resets the tail of the linked list.*/
void resetTail()
{
    if(lwpHead != NULL){
        lwpCur = lwpHead;
        while(lwpCur->next != NULL)
        {
            lwpCur = lwpCur->next;
        }
    }
}

/* LWP add is a function that adds a lwp pid to a linked list.*/
void lwpAdd(int pid)
{ 
    /* If no nodes have been added to the linked list
     * This means we are in ann empty linked list.*/
    if(lwpHead == NULL)
    {
        /* Allocate memory to lwp linked list*/
        lwpHead = (lwpNode *) malloc(sizeof(lwpNode));
        /* Add our pid to our head.*/
        lwpHead->lwpPid = pid;
        /* Set next node to Nulll.*/
        lwpHead->next = NULL;
        /* Make lwp head and cur point to each other.*/
        lwpCur = lwpHead;
    }
    else
    {
        /* Create a new Node to inseart into the linked list.*/
        lwpNode *newNode = (lwpNode *) malloc(sizeof(lwpNode));
        /* Set the newNode pid.*/
        newNode->lwpPid = pid;
        /* Point new node next to NULL.*/
        newNode->next = NULL;
        /* Point the last node to the new node.*/
        lwpCur->next = newNode;
        /* Move the cur over.*/
        lwpCur = newNode;
    }
}

void lwpDelete(int pid)
{
    /* Setting up a cur to iterate through linked list.*/
    lwpNode *cur = lwpHead;
    if(lwpHead == NULL)
    {
        lwpHead = NULL;
    }
    /* if PID == head then we will be removing from the head.*/
    if(pid == lwpHead->lwpPid)
    {
        /* Make sure you are able to delete a node.*/
        if(cur != NULL)
        {
            /* Always removing from the head. Move head to next node.*/
            lwpHead = cur->next;
            /* unlink cur from linked list.*/
            cur->next = NULL;
            /* Free up the node.*/
            free(cur);
        }
    }

    /* Find the node to remove.*/
    else
    {
        lwpNode *prev = lwpHead; 
        /* Loop until you find the node with the same PID.*/
        while((cur->lwpPid != pid) && (cur->next != NULL))
        { 
            /* Holds the previous node*/
            prev = cur;
            /* move the cur over to the next node.*/
            cur = cur->next;
        }
        
        /* Check to see if found the targeted node.*/
        if(cur->lwpPid == pid)
        {
            /* The Prev next node points to cur's next node.*/
            prev->next = cur->next;
            /* unlink cur next from linked list.*/
            cur->next = NULL;
            /* Free up the node.*/
            free(cur);
        }       
    }   
}

int rrScheduling()
{
    if(lwpHead == NULL)
    {
        lwp_exit();
    }

    /* get the pid from the current running lwp.*/
    int runlwp = lwpHead->lwpPid;
    /* delete the curr lwp from linked list.*/
    lwpDelete(runlwp);

    /* add the current lwp back to the end of the linked list.*/
    lwpAdd(runlwp); 
   
return runlwp;
}

/* Function used to get the running LWP.*/
lwp_context *getScheduledLWP()
{
    if(lwpCount == 0)
    {
        return NULL;
    }
    /* If sheduler is not set or null, run round robin scheduling.*/
    if(scheduler == NULL)
    {
        lwp_running = rrScheduling();
    }
    /* else run prededined scheduling alg.*/
    else
    {
        lwp_running = (*scheduler)();
    }
    /* Return the lwp that will be running*/
    return &processTable[lwp_running - offset];
}
/* Creates a new lightweight process which calls the given function with 
 * the given line asrghument
 *
 * returns the new light wight process PID of the new thread 
 * or -1 if more than  LWP_PROC_LIMIT threads all ready exist.*/
extern int  new_lwp(lwpfun func,void *args,size_t stacksize)
{
    /* Check to see if lwp threads exceed LWP_PROC_LIMIT created.*/   
    if(lwpCount > LWP_PROC_LIMIT)
    {
        return -1;
    }

    ptr_int_t *threadStack = (ptr_int_t *) malloc(sizeof(ptr_int_t) * stacksize);
    ptr_int_t *fakeStack = (ptr_int_t *) malloc(sizeof(ptr_int_t) * stacksize);
    ptr_int_t *sp = NULL;
 
    /* Creates a new context.*/
    lwp_context *newLWP = (lwp_context *) malloc(sizeof(lwp_context));      
    /* Check to see if we successfully created a new thread.*/
    if(newLWP == NULL)
    {
        perror("Faled to create new thread");
        exit(-1);
    }
    
    /* Add new threads process id.*/
    newLWP->pid = lwpCount + 1;
    /* Add the size of the stack.*/
    newLWP->stacksize = stacksize;
    /* Add a pointer to the real stack.*/
    newLWP->stack = threadStack;
    
    /* write Stack pointer.*/
    fakeStack = threadStack + stacksize;
    /* Push args to stack*/
    *fakeStack = (ptr_int_t) args;
    fakeStack --;
    /* Push lwp_exit to stack.*/
    *fakeStack = (ptr_int_t) lwp_exit;
    fakeStack --;
    /* Push func to stack.*/
    *fakeStack = (ptr_int_t) func;
     fakeStack --;
    /* Pushed a bougus value. I set this to 0 for debugging purpose.*/
    *fakeStack = 0x2019;
     /* Saving the bogus value as a Sp.*/
     sp = fakeStack;
     fakeStack --;
     /* 6 bogus registers.*/
     *fakeStack = 0x01;
     fakeStack --;
     *fakeStack = 0x02;
     fakeStack --;
     *fakeStack = 0x03;
     fakeStack --;
     *fakeStack = 0x04;
     fakeStack --;
     *fakeStack = 0x05;
     fakeStack --;
     *fakeStack = 0x06;
     fakeStack --;
     /* Pushing the SP to the stack*/
     *fakeStack = (ptr_int_t) sp;

    newLWP->sp = fakeStack;
    /* Add new lwp thread to linked list.*/
    lwpAdd(newLWP->pid);  
    /* Add new lwp thread to process table.*/
    processTable[lwpCount++] = *newLWP;
    
return newLWP->pid;
}

/* Terminates the current LWP, free iuts resources, and moves all the
 * others up in the process table. If there are no other threads,
 * call lwp_stop(). */
extern void lwp_exit()
{
    /* Remove from the processTable.*/
    int i;
    int idxPid = curLwp->pid;
    for(i = idxPid - offset; i < lwpCount; i++)
    {
        processTable[i] = processTable[i + 1];
    }
    
    offset++;
    lwpCount--;
    free(curLwp->stack);
    /* Delete current running lwp.*/
    lwpDelete(idxPid);
    /* Reset the tail of the linked list.*/
    resetTail();
    /* Get new lwp.*/
    curLwp = getScheduledLWP();
    
    /* Check if their is a new lwp.*/
    if(curLwp != NULL)
    {
        /* Set stack pointer to new lwp sp.*/
        SetSP(curLwp->sp);
        /* Restore current lwp context.*/
        RESTORE_STATE();
    }
    /* If no new lwp we stop the threading library.*/
    else
    {
        /* Stop lwp.*/
        lwp_stop();
    }
}

/* Returns the pid of the calling LWP.
 * The return value of lwp_getpid() is undefined if not called by a LWP.*/
extern int lwp_getpid()
{
    if(curLwp == NULL)
    {
        return -1;
    }
return curLwp->pid;
}

/* Yileds  control to another LWP. Which one depends on the scheduler
 * Saves the current LWP's context, picks the next one, restores that 
 * threads context and returns.*/
extern void lwp_yield()
{
    if(lwpCount != 0)
    {
        /* Saves the current LWP context.*/
        SAVE_STATE();
        /* Saves current LWP sp pointer.*/
        GetSP(curLwp->sp);
       /* get next lwp thread*/
        curLwp = getScheduledLWP();       
        /* Set Stack pointer of current running lwp.*/
        SetSP(curLwp->sp);
        /* Restore current lwp context.*/
        RESTORE_STATE();       
    }

}

/* Starts the LWP system. Saves the original context and stack pointer
 * picks a LWP and starts it running. 
 * If there are no LWP's return immidiately.*/
extern void lwp_start()
{
    if(lwpCount != 0)
    {
        /* Saves the original context.*/
        SAVE_STATE();
        /* Saves the original stack pointer to pStack.*/
        GetSP(pStack);
        /* get lwp thread*/
        curLwp = getScheduledLWP();       
        /* Set Stack pointer of current running lwp.*/
        SetSP(curLwp->sp);
        /* Restore current lwp context.*/
        RESTORE_STATE();       
    }
}

/* Stops the LWP System, retores the original stack pointer 
 * and returns to that context.*/
extern void lwp_stop()
{
    /* Restores original stack pointer.*/
    SetSP(pStack);
    /* Restor the original context.*/
    RESTORE_STATE();
}

/* Causes the LWP package to use the function scheduler to choose the next
 * process to run. If scheduler is NULL, or has never been set, 
 * the scheduler should do round robin schdualing.*/
extern void lwp_set_scheduler(schedfun sched)
{
    /* Check to see if their all ready exist a scheduler.*/
    if(sched == 0)
    {
        scheduler = (schedfun *) malloc(sizeof(schedfun));
    }   
    *scheduler = sched;
    
}


