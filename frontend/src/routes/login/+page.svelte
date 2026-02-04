<script lang="ts">
    import { page } from "$app/stores";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import { Checkbox } from "$lib/components/ui/checkbox";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";

    let username = $state("");
    let password = $state("");
    let error = $state("");
    let isLoading = $state(false);
    let rememberMe = $state(false);

    async function handleLogin() {
        isLoading = true;
        error = "";
        const next = $page.url.searchParams.get("next");

        try {
            const res = await fetch("http://localhost:8000/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
                credentials: "include",
            });

            if (res.ok) {
                if (next) {
                    window.location.href = next;
                } else {
                    error = "Login successful, but no redirect URL provided.";
                }
            } else {
                const data = await res.json();
                error = data.detail || "Invalid credentials";
            }
        } catch (e) {
            error = "Login failed. Please check your network connection.";
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <Card class="w-full max-w-md">
        <CardHeader class="space-y-1">
            <CardTitle class="text-2xl text-center">Welcome back</CardTitle>
            <CardDescription class="text-center">
                Enter your credentials to access your account
            </CardDescription>
        </CardHeader>
        <CardContent class="grid gap-4">
            {#if error}
                <div
                    class="bg-destructive/15 text-destructive text-sm p-3 rounded-md text-center"
                >
                    {error}
                </div>
            {/if}
            <div class="grid gap-2">
                <Label for="username">Username</Label>
                <Input
                    id="username"
                    type="text"
                    placeholder="demo"
                    bind:value={username}
                />
            </div>
            <div class="grid gap-2">
                <Label for="password">Password</Label>
                <Input
                    id="password"
                    type="password"
                    placeholder="••••"
                    bind:value={password}
                />
            </div>
            <div class="flex items-center space-x-2">
                <Checkbox id="remember" bind:checked={rememberMe} />
                <Label
                    for="remember"
                    class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                    Remember me
                </Label>
            </div>
        </CardContent>
        <CardFooter class="flex flex-col gap-4">
            <Button class="w-full" onclick={handleLogin} disabled={isLoading}>
                {#if isLoading}
                    <span
                        class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
                    ></span>
                {/if}
                Sign In
            </Button>
            <p class="text-xs text-center text-muted-foreground">
                Demo Credentials: <span class="font-mono bg-muted px-1 rounded"
                    >demo</span
                >
                / <span class="font-mono bg-muted px-1 rounded">demo</span>
            </p>
        </CardFooter>
    </Card>
</div>
