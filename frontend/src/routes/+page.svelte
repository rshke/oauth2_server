<script lang="ts">
    import { onMount } from "svelte";

    // Configuration
    const CLIENT_ID = "frontend_client";
    const REDIRECT_URI = "http://localhost:5173/callback";
    const AUTH_URL = "http://localhost:8000/authorize";

    function login() {
        const params = new URLSearchParams({
            response_type: "code",
            client_id: CLIENT_ID,
            redirect_uri: REDIRECT_URI,
            scope: "read",
            state: "random_state_string",
        });
        window.location.href = `${AUTH_URL}?${params.toString()}`;
    }
</script>

<div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h1 class="text-2xl font-bold mb-6 text-center">OAuth2 Client Demo</h1>
        <p class="mb-4 text-gray-700">Click below to start the OAuth2 flow.</p>
        <button
            on:click={login}
            class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition duration-200"
        >
            Login with OAuth2 Server
        </button>
    </div>
</div>
