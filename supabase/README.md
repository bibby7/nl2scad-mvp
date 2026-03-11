# Supabase Edge Function: Waitlist Email Notifications

This uses a DB trigger to call the Edge Function on each new waitlist row.

## 1) Create the function
From the repo root:

```bash
supabase functions new send-waitlist-email
```

Replace the generated `index.ts` with `supabase/functions/send-waitlist-email/index.ts` from this repo.

## 2) Set secrets
```bash
supabase secrets set \
  RESEND_API_KEY=REPLACE_ME \
  WAITLIST_NOTIFY_TO=bibby7@zohomail.com \
  WAITLIST_FROM_EMAIL=onboarding@resend.dev
```

## 3) Deploy
```bash
supabase functions deploy send-waitlist-email
```

## 4) Create trigger (run in SQL editor)
```sql
create or replace function public.notify_waitlist_signup()
returns trigger
language plpgsql
as $$
begin
  perform
    net.http_post(
      url := 'https://YOUR_PROJECT_REF.supabase.co/functions/v1/send-waitlist-email',
      headers := jsonb_build_object('Content-Type','application/json','Authorization','Bearer ' || current_setting('request.jwt.claims', true)::json->>'sub'),
      body := jsonb_build_object('record', row_to_json(NEW))
    );
  return NEW;
end;
$$;

create trigger trg_waitlist_email
after insert on public.waitlist
for each row execute function public.notify_waitlist_signup();
```

> Replace `YOUR_PROJECT_REF` with your project ref (in URL: https://<ref>.supabase.co)

## 5) Test
Insert a row into `waitlist` and confirm you receive the email.
