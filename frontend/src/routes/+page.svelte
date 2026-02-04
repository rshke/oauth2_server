<script lang="ts">
    import { Button } from "$lib/components/ui/button";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";
    import Shield from "lucide-svelte/icons/shield";
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <Card class="w-full max-w-md text-center">
        <CardHeader>
            <div
                class="mx-auto bg-primary/10 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4"
            >
                <Shield class="w-10 h-10 text-primary" />
            </div>
            <CardTitle class="text-3xl font-bold">OAuth2 Server</CardTitle>
            <CardDescription class="text-lg mt-2">
                Secure, Scalable, and Modern Authentication
            </CardDescription>
        </CardHeader>
        <CardContent>
            <p class="text-muted-foreground mb-6">
                A robust OAuth2 provider built with FastAPI and SvelteKit.
                Managed easily with modern tools.
            </p>
        </CardContent>
        <CardFooter class="flex flex-col gap-4">
            <Button class="w-full text-lg h-12" href="/login">
                Get Started
            </Button>
            <Button
                variant="outline"
                class="w-full"
                href="http://localhost:8000/docs"
            >
                API Documentation
            </Button>
        </CardFooter>
    </Card>
</div>
