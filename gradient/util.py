from enum import Enum 

class FormEnum(Enum):
  '''
  Extended Enum with WTForms helpers
  '''

  @classmethod
  def choices(cls):
    return [(choice, cls._display(cls, choice.name)) for choice in cls]

  @classmethod
  def coerce(cls, item):
    return cls(int(item)) if not isinstance(item, cls) else item

  def __str__(self):
    return str(self.value)

  def _display(self, name):
    ''' 
    converts enum name to displayable string
    ex. "NOT_MARRIED" --> "Not Married"
    '''
    return name.replace("_", " ").title()


StateCodes = (
  ('AL', 'Alabama (AL)'),
  ('AK', 'Alaska (AK)'),
  ('AZ', 'Arizona (AZ)'),
  ('AR', 'Arkansas (AR)'),
  ('CA', 'California (CA)'),
  ('CO', 'Colorado (CO)'),
  ('CT', 'Connecticut (CT)'),
  ('DE', 'Delaware (DE)'),
  ('DC', 'District Of Columbia (DC)'),
  ('FL', 'Florida (FL)'),
  ('GA', 'Georgia (GA)'),
  ('HI', 'Hawaii (HI)'),
  ('ID', 'Idaho (ID)'),
  ('IL', 'Illinois (IL)'),
  ('IN', 'Indiana (IN)'),
  ('IA', 'Iowa (IA)'),
  ('KS', 'Kansas (KS)'),
  ('KY', 'Kentucky (KY)'),
  ('LA', 'Louisiana (LA)'),
  ('ME', 'Maine (ME)'),
  ('MD', 'Maryland (MD)'),
  ('MA', 'Massachusetts (MA)'),
  ('MI', 'Michigan (MI)'),
  ('MN', 'Minnesota (MN)'),
  ('MS', 'Mississippi (MS)'),
  ('MO', 'Missouri (MO)'),
  ('MT', 'Montana (MT)'),
  ('NE', 'Nebraska (NE)'),
  ('NV', 'Nevada (NV)'),
  ('NH', 'New Hampshire (NH)'),
  ('NJ', 'New Jersey (NJ)'),
  ('NM', 'New Mexico (NM)'),
  ('NY', 'New York (NY)'),
  ('NC', 'North Carolina (NC)'),
  ('ND', 'North Dakota (ND)'),
  ('OH', 'Ohio (OH)'),
  ('OK', 'Oklahoma (OK)'),
  ('OR', 'Oregon (OR)'),
  ('PA', 'Pennsylvania (PA)'),
  ('RI', 'Rhode Island (RI)'),
  ('SC', 'South Carolina (SC)'),
  ('SD', 'South Dakota (SD)'),
  ('TN', 'Tennessee (TN)'),
  ('TX', 'Texas (TX)'),
  ('UT', 'Utah (UT)'),
  ('VT', 'Vermont'),
  ('VA', 'Virginia'),
  ('WA', 'Washington'),
  ('WV', 'West Virginia'),
  ('WI', 'Wisconsin'),
  ('WY', 'Wyoming'),
  ('AS', 'American Samoa (AS)'),
  ('GU', 'Guam (GU)'),
  ('MP', 'Northern Mariana Islands (MP)'),
  ('PR', 'Puerto Rico (PR)'),
  ('UM', 'United States Minor Outlying Islands (UM)'),
  ('VI', 'Virgin Islands (VI)')
)

