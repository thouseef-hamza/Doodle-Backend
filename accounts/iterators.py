class ADMINIterator:
     def __iter__(self):
          self.x= 1
          return self
     
     def __next__(self):
          n = "ADMIN %04d" % self.x  
          self.x += 1  
          return n
     
     
class StudentIterator:
     def __iter__(self):
          self.x= 1
          return self
     
     def __next__(self):
          n = "STU %05d" % self.x  
          self.x += 1  
          return n
