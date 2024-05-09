import asyncio
import threading


class ThreadManager:
    @staticmethod
    def start(thread_id, thread_target) -> threading.Thread:
        task = ThreadManager.get_thread(thread_id, thread_target)
        task.start()
        return task

    @staticmethod
    def stop(thread_id, thread_target):
        task = ThreadManager.get_thread(thread_id, thread_target)
        if task.is_alive():
            task.join()

    @staticmethod
    def get_thread(thread_id, thread_target) -> threading.Thread:
        if thread_id > 0: # Threads that are not running have an id of -1
            for thread in threading.enumerate():
                if thread.ident == thread_id:
                    return thread
            
            print("Thread not running, but not found")
        print("Creating new thread")

        return threading.Thread(target=asyncio.run, args=(thread_target,))