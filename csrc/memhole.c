#include "memhole.h"

memhole_t* create_memhole(){
    memhole_t* ret_val = (memhole_t*) calloc(1, sizeof(memhole_t));
    if(!ret_val) return 0;
    ret_val->fd = 0;
    ret_val->buf_size = 0;
    //ret_val->op_sem = {};
    ret_val->self_pointer = ret_val;
    ret_val->buffer = 0;
    return ret_val;
}

int delete_memhole(memhole_t* memhole){
    if(memhole == NULL) return -EINVDEV;
    free(memhole->self_pointer);
    return 0;
}

int connect_memhole(memhole_t* memhole){
    #ifdef MEMHOLEW_ALLOW_WRITE
    int mode = O_RDWR;
    #endif
    #ifndef MEMHOLEW_ALLOW_WRITE
    int mode = O_RDONLY;
    #endif
    #ifdef MEMHOLEW_CLOSE_ON_EXEC
    mode = mode | O_CLOEXEC;
    #endif

    if(memhole == NULL) return -EINVDEV;
    if(access(MEMHOLE_PATH, F_OK)) return -EMEMHNF;

    int ret = open(MEMHOLE_PATH, mode);

    if(ret < 0){
        return -EMEMBSY;
    }
    memhole->fd = ret;
    memhole->buf_size = -1;
    sem_init(&memhole->op_sem, 0, 1);
    return 0;
}

int disconnect_memhole(memhole_t* memhole){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd == 0) return -EINVDEV;
    return close(memhole->fd);
}

long attach_to_pid(memhole_t* memhole, int pid){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd <= 0) return -EINVDEV;
    if(kill(pid, 0)) return -EINVPID;

    long ret = lseek64(memhole->fd, pid, LSMSPID);
    if(ret == 0){
        return -EINVPID;
    }
    return 0;
}

long set_memory_position(memhole_t* memhole, void* pos, memhole_mode_t mode){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd <= 0) return -EINVDEV;
    if(mode == SKMSAFE){
        sem_wait(&memhole->op_sem);
    }
    else if(mode == SKMSFNB){
        if(sem_trywait(&memhole->op_sem)){
            return -EMEMBSY;
        }
    }
    else if(mode != SKMFAST){
        printf("invalid mode used for set_memory_position()\n");
        return -EINVDEV;
    }
    return lseek64(memhole->fd, (long) pos, LSMSPOS);
}

long get_memory_position(memhole_t* memhole){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd <= 0) return -EINVDEV;

    return lseek64(memhole->fd, 0, LSMGPOS);
}

long set_buffer_size(memhole_t* memhole, long len){
    if(len > memhole->buf_size){
        if(lseek64(memhole->fd, len, LSMSBUF)){
            return -EKMALOC;
        }
        memhole->buf_size = len;
    }
    return 0;
}

long read_memory(memhole_t* memhole, char* buf, long len, memhole_mode_t mode){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd <= 0) return -EINVDEV;
    if(!((mode == SKMSAFE) | (mode == SKMFAST) | (mode == SKMSFNB))){
        printf("invalid mode used in read_memory()\n");
        return -EINVDEV;
    }
    if(set_buffer_size(memhole, len)){
        return -EKMALOC;
    }
    long ret_val = read(memhole->fd, buf, len);
    if(mode & (SKMSAFE | SKMSFNB)){
        sem_post(&memhole->op_sem);
    }
    return ret_val;
}

#ifdef MEMHOLEW_ALLOW_WRITE
long write_memory(memhole_t* memhole, char* buf, long len, memhole_mode_t mode){
    if(memhole == NULL) return -EINVDEV;
    if(memhole->fd <= 0) return -EINVDEV;
    if(!((mode == SKMSAFE) | (mode == SKMFAST) | (mode == SKMSFNB))){
        printf("invalid mode used in write_memory()\n");
        return -EINVDEV;
    }
    if(set_buffer_size(memhole, len)){
        return -EKMALOC;
    }
    long ret_val = write(memhole->fd, buf, len);
    if(mode & (SKMSAFE | SKMSFNB)){
        sem_post(&memhole->op_sem);
    }
    return ret_val;
}
#endif