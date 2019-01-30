BEGIN TRANSACTION;
CREATE TABLE "Users" (
	`ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`User_Name`	TEXT NOT NULL UNIQUE,
	`User_Password`	TEXT NOT NULL
);
INSERT INTO `Users` VALUES (1,'ani','Password1');
INSERT INTO `Users` VALUES (2,'ani2','Password2');
INSERT INTO `Users` VALUES (3,'ani3','Password3');
INSERT INTO `Users` VALUES (4,'ani4','Passwor4');
INSERT INTO `Users` VALUES (5,'ani5','Password5');
INSERT INTO `Users` VALUES (6,'ani6','Passwor6');
INSERT INTO `Users` VALUES (7,'ani7','Password7');
INSERT INTO `Users` VALUES (8,'ani8','Password8');
INSERT INTO `Users` VALUES (9,'ani9','Password9');
INSERT INTO `Users` VALUES (10,'ani10','Password10');
INSERT INTO `Users` VALUES (11,'ani11','Password11');
INSERT INTO `Users` VALUES (12,'ani12','Password12');
CREATE TABLE "Threads" (
	`Forum_ID`	INTEGER NOT NULL,
	`Thread_ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`User_ID`	INTEGER NOT NULL,
	`TimeStamp`	DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP UNIQUE,
	`Title`	TEXT NOT NULL,
	FOREIGN KEY(`Forum_ID`) REFERENCES Discussion_Forum ( id ),
	FOREIGN KEY(`User_ID`) REFERENCES Users ( ID )
);
INSERT INTO `Threads` VALUES (1,1,1,'2018-09-24 02:19:49','Old or new?');
INSERT INTO `Threads` VALUES (1,2,2,'2018-09-24 02:20:05','Best color for a car?');
INSERT INTO `Threads` VALUES (2,3,3,'2018-09-24 02:20:25','Best destination?');
INSERT INTO `Threads` VALUES (3,4,4,'2018-09-24 02:22:40','Best dish?');
INSERT INTO `Threads` VALUES (4,5,4,'2018-09-24 02:23:24','Best Language?');
CREATE TABLE "Thread_Posts" (
	`Thread_ID`	INTEGER NOT NULL,
	`Post_ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`Text_V`	TEXT NOT NULL,
	`User_ID`	INTEGER NOT NULL,
	FOREIGN KEY(`Thread_ID`) REFERENCES Threads ( Thread_ID ),
	FOREIGN KEY(`User_ID`) REFERENCES Users ( ID )
);
INSERT INTO `Thread_Posts` VALUES (1,1,'New!!',1);
INSERT INTO `Thread_Posts` VALUES (2,2,'BLue!!',2);
INSERT INTO `Thread_Posts` VALUES (4,3,'PIZZA!!',3);
INSERT INTO `Thread_Posts` VALUES (3,4,'Switzerland!',4);
INSERT INTO `Thread_Posts` VALUES (1,5,'OLD!',1);
INSERT INTO `Thread_Posts` VALUES (3,6,'LA!!!',2);
CREATE TABLE Discussion_Forum (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
Forum_Name TEXT NOT NULL,
User_ID INTEGER NOT NULL,
FOREIGN KEY(User_ID) REFERENCES Users(ID)
);
INSERT INTO `Discussion_Forum` VALUES (1,'Cars',3);
INSERT INTO `Discussion_Forum` VALUES (2,'Travel',4);
INSERT INTO `Discussion_Forum` VALUES (3,'Food',1);
INSERT INTO `Discussion_Forum` VALUES (4,'Programming',2);
INSERT INTO `Discussion_Forum` VALUES (5,'Plane',3);
INSERT INTO `Discussion_Forum` VALUES (6,'Hiking',1);
INSERT INTO `Discussion_Forum` VALUES (7,'cassandra',1);
COMMIT;
