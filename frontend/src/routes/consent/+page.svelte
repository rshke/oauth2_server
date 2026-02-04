<script lang="ts">
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import { Button } from "$lib/components/ui/button";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";
    import Lock from "lucide-svelte/icons/lock";
    import ShieldCheck from "lucide-svelte/icons/shield-check";

    let params: any = $state({});
    let error = $state("");
    let isLoading = $state(false);

    onMount(() => {
        params = Object.fromEntries($page.url.searchParams);
    });

    async function approve() {
        isLoading = true;
        try {
            const res = await fetch("http://localhost:8000/authorize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ...params, confirm: "true" }),
                credentials: "include",
            });

            const data = await res.json();

            if (data.redirect_to) {
                window.location.href = data.redirect_to;
            } else {
                error = "Authorization failed. Please try again.";
                isLoading = false;
            }
        } catch (e) {
            error = "Request failed. Check backend connection.";
            isLoading = false;
        }
    }

    function deny() {
        // In a real app, you would redirect back to client with error=access_denied
        alert("Access Denied. Redirecting to home (Simulation).");
        window.location.href = "/login";
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <Card class="w-full max-w-lg">
        <CardHeader class="text-center">
            <div
                class="mx-auto bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4"
            >
                <Lock class="w-10 h-10 text-primary" />
            </div>
            <CardTitle class="text-2xl">Authorization Request</CardTitle>
            <CardDescription>Secure Access Control</CardDescription>
        </CardHeader>
        <CardContent class="space-y-6">
            <div class="text-center">
                <p class="text-muted-foreground">
                    The application <strong class="text-foreground text-lg"
                        >{params.client_id || "Unknown App"}</strong
                    >
                    <br />
                    wants to access your account:
                </p>
            </div>

            <div class="bg-muted/50 border rounded-xl p-5">
                <h3
                    class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3"
                >
                    Permissions Requested
                </h3>
                <ul class="space-y-3">
                    {#if params.scope}
                        {#each params.scope.split(" ") as scope}
                            <li class="flex items-start">
                                <ShieldCheck
                                    class="h-5 w-5 text-green-500 mr-2 mt-0.5"
                                />
                                <span class="text-sm font-medium">{scope}</span>
                            </li>
                        {/each}
                    {:else}
                        <li
                            class="flex items-center text-muted-foreground italic text-sm"
                        >
                            No specific scopes requested
                        </li>
                    {/if}
                </ul>
            </div>

            {#if error}
                <div
                    class="bg-destructive/15 text-destructive text-sm p-3 rounded-md text-center"
                >
                    {error}
                </div>
            {/if}
        </CardContent>
        <CardFooter class="flex flex-col sm:flex-row gap-4">
            <Button variant="outline" class="w-full sm:w-1/2" onclick={deny}>
                Cancel
            </Button>
            <Button
                class="w-full sm:w-1/2"
                onclick={approve}
                disabled={isLoading}
            >
                {#if isLoading}
                    <span
                        class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
                    ></span>
                    Processing...
                {:else}
                    Approve Access
                {/if}
            </Button>
        </CardFooter>
        <div class="p-6 pt-0 text-center">
            <p class="text-xs text-muted-foreground">
                You will be redirected back to {params.redirect_uri ||
                    "the application"}.
            </p>
        </div>
    </Card>
</div>
