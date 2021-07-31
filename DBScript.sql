--drop table tblcommentsbybot

create table tblcommentsbybot(
id serial PRIMARY KEY, 
comment_id text, 
author text, 
searchtext text, 
reply text, 
added_on text
)

--select * from saminsurance

create table saminsurance(
quote integer,
client text,
risk integer,
recommended text,
selected text,
covertype integer,
finalId integer
)
select * from saminsurance 
insert into saminsurance values(14157,'c1',2804,'Y','Y',120,NULL);
insert into saminsurance values(14157,'c1',2805,'N','N',121,NULL);
insert into saminsurance values(14166,'c1',2806,'Y','N',120,NULL);
insert into saminsurance values(14166,'c1',2807,'N','N',121,NULL);

insert into saminsurance values(14174,'c1',2808,'Y','N',120,NULL);
insert into saminsurance values(14174,'c1',2809,'N','Y',121,NULL);

insert into saminsurance values(14175,'c1',2810,'N','N',120,NULL);
insert into saminsurance values(14175,'c1',2811,'Y','Y',121,NULL);

delete from saminsurance where quote=14174

alter table saminsurance add column modified_date timestamp default now()
select quote,client,covertype
from saminsurance 
where selected='Y' or (selected='N' and recommended='Y' )

select quote,client
,case when decision = 'NY'or decision = 'YN' 
then (select covertype from saminsurance where selected='Y' and quote=T.quote and client = T.client limit 1)
else (select covertype from saminsurance where selected='N' and recommended='Y' and quote=T.quote and client = T.client limit 1) end as "FinalCoverId"
FROM
(select quote,client,string_agg(distinct selected,'') as "decision"
from saminsurance 
group by quote,client) as T




update saminsurance set modified_date='2020-07-22 16:12:47' where quote=14166;
update saminsurance set modified_date='2020-07-23 16:12:47' where quote=14174;
update saminsurance set modified_date='2020-07-10 16:12:47' where quote=14175;



