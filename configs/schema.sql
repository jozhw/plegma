-- tags; first two elements of id are ta
CREATE TABLE tags (
       id TEXT PRIMARY KEY UNIQUE,
       tag_name TEXT NOT NULL,
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime
);

-- persons; first two elements of id are pe; this will serve as the nexus along with entity
CREATE TABLE persons (
       id TEXT PRIMARY KEY UNIQUE,
       first_name TEXT NOT NULL,
       last_name TEXT NOT NUll,
       middle_name TEXT,
       preferred_name TEXT,
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime
);

-- entities; first two elements of id are en; this will serve as the nexus along with person
CREATE TABLE entities (
       id TEXT PRIMARY KEY UNIQUE,
       entity_name TEXT NOT NULL,
       preferred_name TEXT,
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime
);

-- signatures; first two elements of id are si; 
CREATE TABLE signatures (
       id TEXT PRIMARY KEY UNIQUE,
       signature TEXT NOT NULL,
       -- the is_person or is_entity will determine if the signature will reference the id of person or entity
       is_person BOOLEAN DEFAULT FALSE, 
       is_entity BOOLEAN DEFAULT FALSE,
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime,

       CHECK (NOT (is_person AND is_entity)) -- Cannot be both person and entity
);

-- addresses; first two elements of id are ad; 
CREATE TABLE addresses (
       id TEXT PRIMARY KEY UNIQUE,
       apartment TEXT,
       current_occupants TEXT, -- will be a list of either entity ids or person ids
       past_occupants TEXT,
       longitude TEXT NOT NULL,
       lattitude TEXT NOT NULL,
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime,
)

-- emails; first two elements of id are em; 
CREATE TABLE emails (
       id TEXT PRIMARY KEY UNIQUE,
       email_address TEXT NOT NULL,
       owner TEXT NOT NULL,
       email_type TEXT DEFAULT 'personal', -- 'personal', 'work', 'other'
       is_active BOOLEAN DEFAULT TRUE, -- if the email is still in use
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime,
)

-- phone_numbers; first two elements of id are ph; 
CREATE TABLE phone_numbers (
       id TEXT PRIMARY KEY UNIQUE,
       phone_number TEXT NOT NULL,
       country_code INTEGER NOT NULL DEFAULT 1,
       phone_number_type TEXT DEFAULT 'personal', -- 'personal', 'work', 'other'
       owner TEXT NOT NULL,
       owner_history TEXT,
       is_active BOOLEAN DEFAULT TRUE, -- if the email is still in use
       description TEXT,
       date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       last_added DATETIME DEFAULT CURRENT_TIMESTAMP,
       update_history TEXT -- will be a list of datetime,
)
