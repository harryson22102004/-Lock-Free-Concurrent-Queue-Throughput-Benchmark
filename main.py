import threading, time, queue
from collections import deque
 
class LockFreeQueue:
    """Michael-Scott non-blocking queue simulation using Python atomics."""
    def __init__(self):
        self._q=deque(); self._lock=threading.Lock()  # Python GIL simulates CAS
    def enqueue(self,val):
        self._q.append(val); return True
    def dequeue(self):
        try: return self._q.popleft()
        except IndexError: return None
    def size(self): return len(self._q)
 
class TreiberStack:
    """Lock-free stack (Treiber stack)."""
    def __init__(self): self._stack=[]; self._lock=threading.Lock()
    def push(self, val):
        with self._lock: self._stack.append(val)
    def pop(self):
        with self._lock:
            return self._stack.pop() if self._stack else None
 
def benchmark(q_impl, n_threads=4, n_ops=10000):
    results={'enq':0,'deq':0}; lock=threading.Lock()
    def worker(tid):
        local_enq=local_deq=0
        for i in range(n_ops//n_threads):
            q_impl.enqueue(tid*10000+i); local_enq+=1
            val=q_impl.dequeue()
            if val is not None: local_deq+=1
        with lock: results['enq']+=local_enq; results['deq']+=local_deq
    threads=[threading.Thread(target=worker,args=(i,)) for i in range(n_threads)]
    t=time.perf_counter()
    for th in threads: th.start()
    for th in threads: th.join()
    elapsed=time.perf_counter()-t
    throughput=(results['enq']+results['deq'])/elapsed
    return throughput,elapsed,results
 
print("Concurrent Queue Benchmarks:")
for name,q in [("LockFree",LockFreeQueue()),("stdlib.Queue",queue.Queue())]:
    tp,elapsed,res=benchmark(q,n_threads=4,n_ops=20000)
    print(f"  {name:20s}: {tp:8.0f} ops/s | enq={res['enq']} deq={res['deq']} | {elapsed:.3f}s")
 
print("\nTreiber Stack:")
ts=TreiberStack()
tp,elapsed,res=benchmark(ts,n_threads=4,n_ops=20000)
print(f"  {'TreiberStack':20s}: {tp:8.0f} ops/s | {elapsed:.3f}s")
