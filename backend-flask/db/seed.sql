INSERT INTO public.users (display_name, handle, cognito_user_id, email)
VALUES
    ('Capt. Picard', 'the_captain', 'MOCK', 'Jean-luc@startrek.net'),
    ('Geralt of Rivia', 'Blaviken_Butcher', 'MOCK', 'WhiteWolf@winterhome.com');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES (
        (SELECT uuid FROM public.users WHERE users.handle = 'BlavikenButcher' LIMIT 1), 
        'This was imported as seed data!!!', 
        current_timestamp + interval '10 day'
)