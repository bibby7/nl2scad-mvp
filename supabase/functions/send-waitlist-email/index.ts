// Supabase Edge Function: send-waitlist-email
// Sends a notification email via Resend when a new waitlist row is inserted.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { Resend } from "https://esm.sh/resend@2.2.0";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY")!;
const TO_EMAIL = Deno.env.get("WAITLIST_NOTIFY_TO")!;
const FROM_EMAIL = Deno.env.get("WAITLIST_FROM_EMAIL")!;

const resend = new Resend(RESEND_API_KEY);

serve(async (req) => {
  try {
    const payload = await req.json();
    const record = payload.record;

    const html = `
      <h2>New waitlist signup</h2>
      <ul>
        <li><strong>Name:</strong> ${record.name || ""}</li>
        <li><strong>Email:</strong> ${record.email || ""}</li>
        <li><strong>Role:</strong> ${record.role || ""}</li>
        <li><strong>Use case:</strong> ${record.usecase || ""}</li>
      </ul>
      <p>Created at: ${record.created_at}</p>
    `;

    await resend.emails.send({
      from: FROM_EMAIL,
      to: TO_EMAIL,
      subject: "New NL→OpenSCAD waitlist signup",
      html,
    });

    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: String(err) }), { status: 500 });
  }
});
