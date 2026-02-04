<script lang="ts">
    import { onMount } from "svelte";
    import { page } from "$app/stores";

    let code: string | null = null;
    let accessToken: string | null = null;
    let protectedData: any = null;
    let error: string | null = null;

    const CLIENT_ID = "frontend_client";
    const CLIENT_SECRET = "secret"; // In real public client, do not store secret. For demo strictly.
    const REDIRECT_URI = "http://localhost:5173/callback";
    const TOKEN_URL = "http://localhost:8000/token";
    const PROTECTED_URL = "http://localhost:8000/protected";

    onMount(async () => {
        const params = new URLSearchParams(window.location.search);
        code = params.get("code");

        if (code) {
            try {
                // Exchange code for token
                const body = new URLSearchParams({
                    grant_type: "authorization_code",
                    code: code,
                    client_id: CLIENT_ID,
                    client_secret: CLIENT_SECRET,
                    redirect_uri: REDIRECT_URI,
                });

                const res = await fetch(TOKEN_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: body,
                });

                if (!res.ok) throw new Error("Failed to get token");

                const data = await res.json();
                accessToken = data.access_token;

                // Access protected resource
                if (accessToken) {
                    const protectedRes = await fetch(PROTECTED_URL, {
                        headers: { Authorization: `Bearer ${accessToken}` },
                    });

                    if (protectedRes.ok) {
                        protectedData = await protectedRes.json();
                    } else {
                        throw new Error("Failed to access protected resource");
                    }
                }
            } catch (e: any) {
                error = e.message;
            }
        }
    });
</script>

<div
    class="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4"
>
    <div class="bg-white p-6 rounded shadow-lg w-full max-w-2xl">
        <h2 class="text-xl font-bold mb-4">Callback Processing</h2>

        {#if error}
            <div class="bg-red-100 text-red-700 p-3 rounded mb-4">
                Error: {error}
            </div>
        {/if}

        <div class="space-y-4">
            <div>
                <span class="font-semibold block">Authorization Code:</span>
                <code class="bg-gray-100 p-1 rounded block overflow-auto"
                    >{code || "Waiting..."}</code
                >
            </div>

            {#if accessToken}
                <div>
                    <span class="font-semibold block">Access Token:</span>
                    <code
                        class="bg-green-100 p-1 rounded block overflow-auto break-all"
                        >{accessToken}</code
                    >
                </div>
            {/if}

            {#if protectedData}
                <div class="mt-4 border-t pt-4">
                    <span class="font-semibold block text-lg mb-2"
                        >Protected Resource Data:</span
                    >
                    <pre
                        class="bg-blue-50 p-3 rounded overflow-auto">{JSON.stringify(
                            protectedData,
                            null,
                            2,
                        )}</pre>
                </div>
            {/if}
        </div>

        <div class="mt-6">
            <a href="/" class="text-blue-500 hover:underline"
                >&larr; Back to Home</a
            >
        </div>
    </div>
</div>
