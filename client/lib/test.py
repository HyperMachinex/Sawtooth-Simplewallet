import ctypes
import json

# Load the shared library
lib = ctypes.CDLL('./accumulator.so')

# Define the return and argument types for the functions
lib.GenerateAccumulator.argtypes = [ctypes.c_int]
lib.GenerateAccumulator.restype = ctypes.c_char_p

lib.AddElement.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
lib.AddElement.restype = ctypes.c_char_p

lib.DeleteElement.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
lib.DeleteElement.restype = ctypes.c_char_p

lib.BatchAddElement.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
lib.BatchAddElement.restype = ctypes.c_char_p

lib.BatchDeleteElement.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
lib.BatchDeleteElement.restype = ctypes.c_char_p

lib.WitnessUpdate.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.WitnessUpdate.restype = ctypes.c_char_p

lib.Verify.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
lib.Verify.restype = ctypes.c_int

class Accumulator:
    def __init__(self, bit_size):
        self.bit_size = bit_size
        accumulator_data = json.loads(lib.GenerateAccumulator(bit_size).decode('utf-8'))
        self.acc = accumulator_data['acc']
        self.acc_core = accumulator_data['acc_core']
        self.aux_r = accumulator_data['aux_r']
        self.aux_n = accumulator_data['aux_n']
        self.g = accumulator_data['g']
        self.p = accumulator_data['p']
        self.sk = accumulator_data['sk']
        self.vk = accumulator_data['vk']
        self.X = '{"element_prime_id_set": []}'

    def add_element(self, element):
        """
        Add an element to the accumulator

        :param element: The element to be added
        :return: The element prime ID, witness core and gx
        """
        add_element_json = lib.AddElement(element.encode('utf-8'), self.acc_core.encode('utf-8'), self.aux_r.encode('utf-8'), self.aux_n, self.g.encode('utf-8'), self.p.encode('utf-8'), self.sk.encode('utf-8'), self.bit_size, None, self.X.encode('utf-8'))
        updated_data = json.loads(add_element_json.decode('utf-8'))
        self.X = updated_data['X']
        self.acc_core = updated_data['acc_core']
        self.acc = updated_data['acc']
        self.aux_r = updated_data['aux_r']
        self.aux_n = updated_data['aux_n']


        return (updated_data['element_prime_id'], updated_data['wit_core'], updated_data['gx'])

    def delete_element(self, element):
        """
        Delete an element from the accumulator

        :param element: The element to be deleted
        :return: The element prime ID, witness core and gx
        """
        try:
            delete_element_json = lib.DeleteElement(element.encode('utf-8'), self.acc_core.encode('utf-8'), self.aux_r.encode('utf-8'), self.aux_n, self.g.encode('utf-8'), self.p.encode('utf-8'), self.sk.encode('utf-8'), self.bit_size, None, self.X.encode('utf-8'))
            updated_data = json.loads(delete_element_json.decode('utf-8'))
            self.X = updated_data['X']
            self.acc_core = updated_data['acc_core']
            self.acc = updated_data['acc']
            self.aux_r = updated_data['aux_r']
            self.aux_n = updated_data['aux_n']

            return True
        except Exception as e:
            print(e)
            return False

    def batch_add_elements(self, batch_elements):
        """
        Add elements in batch to the accumulator

        :param batch_elements: The elements to be added in batch
        :return: The updated accumulator data {gx: gx, wit_core: wit_core, element_prime_id_set: element_prime_id_set}
        """
        # turn batch elements to josn inside batch_set
        batch_set = {
            'batch_set': [element.decode('utf-8') if isinstance(element, bytes) else element for element in batch_elements]
        }

        batch_elements = json.dumps(batch_set)

        batch_add_json = lib.BatchAddElement(batch_elements.encode('utf-8'), self.acc_core.encode('utf-8'), self.aux_r.encode('utf-8'), self.aux_n, self.g.encode('utf-8'), self.p.encode('utf-8'), self.sk.encode('utf-8'), self.bit_size, None, self.X.encode('utf-8'))
        updated_data = json.loads(batch_add_json.decode('utf-8'))
        self.X = updated_data['X']
        self.acc_core = updated_data['acc_core']
        self.aux_r = updated_data['aux_r']
        self.aux_n = updated_data['aux_n']

        print(updated_data)
        print("\n")
        update_result = updated_data['update_result']
        update_result = json.loads(update_result)
        update_result = update_result['update_result']
        print(update_result)
        print("\n")
        
        return update_result

    def batch_delete_elements(self, batch_elements):
        """
        Delete elements in batch from the accumulator

        :param batch_elements: The elements to be deleted in batch
        :return: The updated accumulator data {gx: gx, wit_core: wit_core, element_prime_id_set: element_prime_id_set}
        """

                # turn batch elements to josn inside batch_set
        batch_set = {
            'batch_set': [batch_elements.decode('utf-8') if isinstance(element, bytes) else element for element in batch_elements]
        }
        
        batch_elements = json.dumps(batch_set)

        batch_delete_json = lib.BatchDeleteElement(batch_elements.encode('utf-8'), self.acc_core.encode('utf-8'), self.aux_r.encode('utf-8'), self.aux_n, self.g.encode('utf-8'), self.p.encode('utf-8'), self.sk.encode('utf-8'), self.bit_size, None, self.X.encode('utf-8'))
        updated_data = json.loads(batch_delete_json.decode('utf-8'))
        self.X = updated_data['X']
        self.acc_core = updated_data['acc_core']
        self.acc = updated_data['acc']
        self.aux_r = updated_data['aux_r']
        self.aux_n = updated_data['aux_n']

        print(updated_data)
        update_result = updated_data['update_result']

        return updated_data
    
    def witness_update(self, element_prime_id):
        """
        Update the witness for an element

        :param element_prime_id: The element prime ID to be updated
        :return: The updated witness core and gx
        """
        witness_update_json = lib.WitnessUpdate(element_prime_id.encode('utf-8'), self.acc_core.encode('utf-8'), self.p.encode('utf-8'), self.g.encode('utf-8'), self.sk.encode('utf-8'), self.X.encode('utf-8'))
        updated_data = json.loads(witness_update_json.decode('utf-8'))

        print(updated_data)

        return (updated_data['wit'], updated_data['gx'])
    
    def verify(self, wit_core, gx):
        """
        Verify an element

        :param wit_core: The witness core
        :param gx: The gx value
        :return: The verification result
        """
        return lib.Verify(self.acc.encode('utf-8'), wit_core.encode('utf-8'), gx.encode('utf-8'), self.vk.encode('utf-8'), self.p.encode('utf-8'))
    
    def get_accumulator(self):
        return {
            'acc': self.acc,
            'acc_core': self.acc_core,
            'aux_r': self.aux_r,
            'aux_n': self.aux_n,
            'g': self.g,
            'p': self.p,
            'sk': self.sk,
            'vk': self.vk,
            'X': self.X
        }
    
# Test the accumulator

# Create an accumulator
acc = Accumulator(256)
print(acc.get_accumulator())
print("\n")

# Add an element to the accumulator
element = "0A58Cd65F0"
element_prime_id, wit_core, gx = acc.add_element(element)
print("Element prime ID: ", element_prime_id)
print("Witness core: ", wit_core)
print("gx: ", gx)
print("\n")

print(acc.get_accumulator())
print("\n")

# Verify the element must return true
verification_result = acc.verify(wit_core, gx)
print("Verification result: ", verification_result)
print("\n")

# Delete the element from the accumulator
delete_result = acc.delete_element(element_prime_id)

print(acc.get_accumulator())
print("\n")

# Verify the element must return false
verification_result = acc.verify(wit_core, gx)
print("Verification result: ", verification_result)
print("\n")

# Batch add elements to the accumulator
batch_elements = ["0A58Cd65F1", "0A58Cd65F2", "0A58Cd65F3"]
updated_data = acc.batch_add_elements(batch_elements)
print("Updated data: ", updated_data)
print("\n")

print(acc.get_accumulator())
print("\n")

# Delete 1 element from the batch
acc_x = acc.get_accumulator()['X']
acc_x = json.loads(acc_x)['element_prime_id_set']
delete_result = acc.delete_element(acc_x[0])
print("\n")

print(acc.get_accumulator())
print("\n")

# After delete verify the remaining elements
acc_x = acc.get_accumulator()['X']
acc_x = json.loads(acc_x)['element_prime_id_set']
for i in range(0, len(acc_x)):
    wit_core, gx = acc.witness_update(acc_x[i])
    verification_result = acc.verify(wit_core, gx)
    print("Verification result: ", verification_result)

# Add new element to the accumulator
element = "0A58Cd65F7"
element_prime_id, wit_core, gx = acc.add_element(element)
print("Element prime ID: ", element_prime_id)
print("Witness core: ", wit_core)
print("gx: ", gx)
print("\n")

print(acc.get_accumulator())
print("\n")

# Batch delete 2 elements inside the acc_x
acc_x = acc.get_accumulator()['X']
acc_x = json.loads(acc_x)['element_prime_id_set']
delete_result = acc.batch_delete_elements(acc_x[0:2])
print("\n")

print(acc.get_accumulator())
print("\n")

# After delete verify the remaining elements
acc_x = acc.get_accumulator()['X']
acc_x = json.loads(acc_x)['element_prime_id_set']
for i in range(0, len(acc_x)):
    wit_core, gx = acc.witness_update(acc_x[i])
    verification_result = acc.verify(wit_core, gx)
    print("Verification result: ", verification_result)
