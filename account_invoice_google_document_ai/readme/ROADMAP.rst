* The attachment decoders hooks (``_get_create_invoice_from_attachment_decoders``
  and ``_get_update_invoice_from_attachment_decoders``) do not exist in 13.0
  core. This module defines them, together with the 14.0 behaviour of
  ``account.journal.create_invoice_from_attachment`` and
  ``account.move._message_post_after_hook``, so they can be reused by other
  decoders.
