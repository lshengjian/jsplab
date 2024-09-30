import itertools
import numpy as np
from sortedcontainers import SortedDict  
from dataclasses import dataclass
from typing import List

@dataclass
class Address:
    street: str
    city: str


@dataclass
class PersonWithAddresses:
    name: str
    age: int
    addresses: List[Address]

def test_dict2data():
   person_dict = {
        'name': 'Bob',
        'age': 40,
        'addresses': [
            {'street': 'First St', 'city': 'City1'},
            {'street': 'Second St', 'city': 'City2'}
        ]
    }
   address_dicts = person_dict['addresses']
   addresses = [Address(**address_dict) for address_dict in address_dicts]
   person = PersonWithAddresses(**{**person_dict, 'addresses': addresses})
   assert 'Bob'==person.name and 40==person.age and 2==len(person.addresses)
   #print(person)
#pip install sortedcontainers
def test_combination():
    data=list(itertools.product([0, 1], repeat=3)) # [0,1] [0,1] [0,1]各取一个的组合是 2*2*2=8
    assert 8==len(data) and (0,0,0)==data[0] and   (1,1,1)==data[7]

def test_orderdict():
    data = SortedDict({1:3,3:1,2:2}) 
    assert list(data.keys()) ==[1,2,3]
    assert list(data.values()) ==[3,2,1]

    sorted_dict = SortedDict()  


    sorted_dict['b'] = 2  
    sorted_dict['a'] = 1  
    sorted_dict['c'] = 3  

    assert list(sorted_dict.keys())==['a', 'b',  'c']

def test_nonzero():
    idxs=np.nonzero([0,1.5,2])[0] # olny one dimetion
    assert [1,2]==idxs.tolist()
