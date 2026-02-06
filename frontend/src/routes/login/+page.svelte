<script lang="ts">
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import { Button } from "$lib/components/ui/button";
    import { Input } from "$lib/components/ui/input";
    import { Label } from "$lib/components/ui/label";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";

    let username = "";
    let password = "";
    let isLoading = false;

    async function handleLogin(event: Event) {
        event.preventDefault();
        isLoading = true;

        try {
            // TODO: Replace with actual backend call
            console.log("Attempting login with:", { username, password });

            // Simulate network delay
            await new Promise((resolve) => setTimeout(resolve, 1000));

            // Mock success
            console.log("Login successful");

            // Preserve query parameters
            const params = $page.url.searchParams.toString();
            const target = params ? `/consent?${params}` : "/consent";
            await goto(target);
        } catch (error) {
            console.error("Login failed", error);
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <Card class="w-[350px]">
        <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>
                Enter your credentials to access your account.
            </CardDescription>
        </CardHeader>
        <CardContent>
            <form onsubmit={handleLogin}>
                <div class="grid w-full items-center gap-4">
                    <div class="flex flex-col space-y-1.5">
                        <Label for="username">Username</Label>
                        <Input
                            id="username"
                            placeholder="Your username"
                            bind:value={username}
                            disabled={isLoading}
                        />
                    </div>
                    <div class="flex flex-col space-y-1.5">
                        <Label for="password">Password</Label>
                        <Input
                            id="password"
                            type="password"
                            placeholder="Your password"
                            bind:value={password}
                            disabled={isLoading}
                        />
                    </div>
                </div>

                <!-- Hidden submit button to enable enter key submission if needed, 
                     though the main button is outside the form in the original design.
                     Structure adjusted to include button in form for semantic correctness -->
                <div class="hidden">
                    <button type="submit">Submit</button>
                </div>
            </form>
        </CardContent>
        <CardFooter class="flex justify-between">
            <Button variant="outline" href="/" disabled={isLoading}
                >Cancel</Button
            >
            <Button onclick={handleLogin} disabled={isLoading}>
                {isLoading ? "Logging inside..." : "Login"}
            </Button>
        </CardFooter>
    </Card>
</div>
