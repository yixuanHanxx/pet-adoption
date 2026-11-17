DROP TABLE IF EXISTS pets;

CREATE TABLE pets(
pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
species TEXT NOT NULL,
name TEXT NOT NULL,
age_group TEXT NOT NULL,
gender TEXT NOT NULL,
availability TEXT NOT NULL,
description TXT NOT NULL,
pic TXT NOT NULL
);

INSERT INTO pets (species, name, age_group, gender, availability, description, pic)
VALUES ('dog','Lucky','baby','boy','available','Lucky is a nature-loving puppy who runs and tumbles on the grass as part of his daily routine.Lucky loves people, likes other dogs, enjoys chasing squirrels, and hates cats.','Lucky.jpg'),
('dog','Owen','baby','boy','available','Owen is a police dog who was fired for being too friendly. His favorite food is chicken thighs.','Owen.jpg'),
('cat','Sanmei','baby','girl','available','Sanmei is very interested in human computers, so if you need to work, you might want to get her a special keyboard.','Sanmei.jpg'),
('cat','Penpen','baby','boy','available','Penpen is a quiet and polite boy who prefers to keep a social distance from humans. But when you say hello to him, he will say hello back.','Penpen.jpg'),
('cat','Qiuqiu','baby','boy','available','Qiuqiu is curious about the world. He likes cats and humans, not dogs. He likes to get into the arms of humans when they are sleeping.','Qiuqiu.jpg'),
('dog','Copper','baby','girl','available','Copper likes ice cream and hates candles. She likes to be around humans she trusts. She always keeps a vigilant eye out for birds.','Copper.jpg'),
('cat','Jojo','baby','girl','available','Jojo likes to go out for walks. Passionate about the world. She loves to play with humans but is afraid of other cats.','Jojo.jpg'),
('dog','Baobao','baby','girl','available','Baobao is an energetic puppy. Needs tons of exercise every day. Friendly to humans.','Baobao.jpg'),
('cat','Cherry','baby','girl','available','Cherry is a quiet kitty. She is curious about every thing that humans eat. Friendly to other kittens.','Cherry.jpg'),
('dog','Chouchou','baby','girl','available','Chouchou is a little princess and has her attitude towards strangers. Loves walks and sunshine and is friendly with other pups.','Chouchou.jpg')
;


DROP TABLE IF EXISTS users;

CREATE TABLE users
(
user_id TEXT PRIMARY KEY,
password TEXT NOT NULL,
admin BOOLEAN DEFAULT 'F' CHECK (admin IN ('F', 'T'))
);

DROP TABLE IF EXISTS applications;

CREATE TABLE applications
(
apl_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT NOT NULL,
pet_id INTEGER NOT NULL,
name TEXT NOT NULL,
firstName TEXT NOT NULL,
lastName TEXT NOT NULL,
address TEXT NOT NULL,
reason TEXT NOT NULL,
status TEXT DEFAULT 'Submitted' CHECK (status IN ('Submitted', 'Processing', 'Completed'))
);

DROP TABLE IF EXISTS volunteers;

CREATE TABLE volunteers
/*(
user_id TEXT PRIMARY KEY,
available_days TEXT NOT NULL,
start_time TIME NOT NULL,
end_time TIME NOT NULL,
admin BOOLEAN DEFAULT 'F' CHECK (admin IN ('F', 'T'))
);
*/
(
user_id TEXT PRIMARY KEY,
apply BOOLEAN DEFAULT 'F' CHECK (admin IN ('F', 'T'))
);

DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
user_id TEXT NOT NULL,
pet_id INTEGER NOT NULL,
name TIME NOT NULL,
review TEXT NOT NULL,
PRIMARY KEY (user_id, pet_id)
);

