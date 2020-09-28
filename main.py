from multiprocessing import Process, Pipe
from os import getpid

def calc_recv_timestamp(recv_time_stamp, counter, pid):
    counter_ = [0] * 3

    for i in range(len(counter)):
        counter_[i] = max(recv_time_stamp[i], counter[i])

    pid_counter = max(recv_time_stamp[pid], counter_[pid]) + 1

    counter_[pid] = pid_counter
    return counter_

def event(pid, counter):
    counter[pid] += 1
    print('Event occured in {}!'.\
          format(pid))
    return counter

def send_message(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(('Some message', counter))

    print('Message sent from ' + str(pid))
    print('Vector clocks: ', str(counter))

    return counter

def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter, pid)

    print('Message received at ' + str(pid))
    print('Vector clocks: ', str(counter))

    return counter

def process_a(pipe_ab):
    pid = 0
    counter = [0, 0, 0]

    counter = send_message(pipe_ab, pid, counter)
    counter = send_message(pipe_ab, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_ab, pid, counter)
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_ab, pid, counter)

    print('-- Final vector clocks values at ', str(pid), ': ', str(counter))

def process_b(pipe_ba, pipe_bc):
    pid = 1
    counter = [0, 0, 0]

    counter = recv_message(pipe_ba, pid, counter)
    counter = recv_message(pipe_ba, pid, counter)
    counter = send_message(pipe_ba, pid, counter)
    counter = recv_message(pipe_bc, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe_ba, pid, counter)
    counter = send_message(pipe_bc, pid, counter)
    counter = send_message(pipe_bc, pid, counter)

    print('-- Final vector clocks values at ', str(pid), ': ', str(counter))

def process_c(pipe_cb):
    pid = 2
    counter = [0, 0, 0]

    counter = send_message(pipe_cb, pid, counter)
    counter = recv_message(pipe_cb, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe_cb, pid, counter)

    print('-- Final vector clocks values at ', str(pid), ': ', str(counter))

if __name__ == '__main__':
    ab, ba = Pipe()
    bc, cb = Pipe()

    process1 = Process(target=process_a,
                       args=(ab,))
    process2 = Process(target=process_b,
                       args=(ba, bc))
    process3 = Process(target=process_c,
                       args=(cb,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()
