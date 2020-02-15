--drop table tblcommentsbybot

create table tblcommentsbybot(
id serial PRIMARY KEY, 
comment_id text, 
author text, 
searchtext text, 
reply text, 
added_on text
)

--select * from tblcommentsbybot
