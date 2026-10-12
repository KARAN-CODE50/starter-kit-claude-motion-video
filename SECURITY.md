# Security

Keep API credentials in a local `.env` file. Only `.env.example`, with an empty key, belongs in Git. The demo and automated tests do not call ElevenLabs or require credentials.

Generated audio, downloaded clips, frame caches, private keys, dependencies and environment files are ignored. `npm run check` checks publishable files for common credential patterns; this is a best-effort check, not a guarantee. Review staged files before every push.

The renderer binds to localhost and serves only its asset directories. Run it with trusted local film code and trusted inputs. Do not expose its HTTP server to a network.

If a credential leaks, revoke it at its provider immediately, then remove it from Git history. Deleting the current file alone does not remove earlier commits. Report vulnerabilities privately through GitHub security advisories when enabled; never put secrets in an issue.
