# Build Assistant

When the user asks to build the project:

1. Check whether `build.bat` exists in the repository root.
2. Execute `build.bat`.
3. Wait for the build to finish.
4. Determine success from the process exit code.
5. If the build fails:
   - Inspect the generated build logs.
   - Explain compiler/build errors.
   - Help resolve the failure.
6. If the build succeeds:
   - Inform the user.
   - Continue with the requested task.

Do not modify the build system unless explicitly requested.