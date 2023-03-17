insert into public.users (display_name, handle, cognito_user_id)
values
  ('Pop Goes the Weasel', 'hotwheels', 'MOCK'),
  ('Fifty Pence', 'getFullOrDieTryin', 'MOCK');

insert into public.activities (user_uuid, message, expires_at)
  values (
    (select uuid from public.users where users.handle = 'hotwheels' limit 1),
    'This was imported as seed data',
    current_timestamp + interval '10 day'
  );