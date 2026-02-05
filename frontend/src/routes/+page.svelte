<script lang="ts">
    import { Button } from "$lib/components/ui/button";
</script>

<div
    class="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-center px-4"
>
    <div class="max-w-2xl space-y-6">
        <h1 class="text-4xl font-extrabold tracking-tight lg:text-5xl">
            Secure Authenticiation for Your Apps
        </h1>
        <p class="text-xl text-muted-foreground">
            A robust, secure, and easy-to-integrate OAuth2 server implementation
            for your modern applications.
        </p>
        <div class="flex justify-center gap-4">
            <Button href="/login" size="lg">Get Started</Button>
            <Button variant="outline" size="lg" href="https://oauth.net/2/"
                >Learn More</Button
            >
        </div>
    </div>
</div>
