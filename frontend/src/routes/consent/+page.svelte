<script lang="ts">
    import { page } from "$app/stores";
    import { Button } from "$lib/components/ui/button";
    import {
        Card,
        CardContent,
        CardDescription,
        CardFooter,
        CardHeader,
        CardTitle,
    } from "$lib/components/ui/card";
    import { Label } from "$lib/components/ui/label";
    import { Checkbox } from "$lib/components/ui/checkbox";

    let isLoading = false;

    async function handleAllow() {
        isLoading = true;
        try {
            console.log("Consent allowed");

            // Gather params from URL
            const searchParams = $page.url.searchParams;
            const params: Record<string, string> = {};
            searchParams.forEach((value, key) => {
                params[key] = value;
            });

            // Default params if missing (for dev/test convenience)
            if (!params.redirect_uri)
                params.redirect_uri = "http://localhost:3000/callback";
            if (!params.client_id) params.client_id = "demo_client";
            if (!params.response_type) params.response_type = "code";

            // Call Backend to Confirm and Get Code
            const response = await fetch("http://localhost:8000/authorize", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(params),
                credentials: "include", // Important: Send cookies with request
            });

            if (!response.ok) {
                if (response.status === 401) {
                    console.warn(
                        "Session expired or invalid, redirecting to login",
                    );
                    const currentUrl = $page.url.toString();
                    window.location.href = `/login?next=${encodeURIComponent(currentUrl)}`;
                    return;
                }

                const errorText = await response.text();
                console.error("Backend error:", response.status, errorText);
                alert(`Authorization failed: ${errorText}`);
                return;
            }

            const data = await response.json();

            if (data.redirect_to) {
                // Redirect browser to the callback URL provided by backend
                console.log("Redirecting to:", data.redirect_to);
                window.location.href = data.redirect_to;
            } else {
                console.error("No redirect_to in response", data);
                alert("Invalid response from server");
            }
        } catch (error) {
            console.error("Error allowing access", error);
            alert("An error occurred during authorization.");
        } finally {
            isLoading = false;
        }
    }

    async function handleDeny() {
        // Just redirect back to client with error or show message
        alert("Access denied. (In real flow, would redirect with error)");
        // window.location.href = "http://localhost:3000/callback?error=access_denied";
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <Card class="w-[450px]">
        <CardHeader>
            <CardTitle>Authorize Application</CardTitle>
            <CardDescription>
                <strong>Example App</strong> wants to access your account.
            </CardDescription>
        </CardHeader>
        <CardContent>
            <div class="flex flex-col space-y-4">
                <p class="text-sm text-gray-500">
                    The application is requesting the following permissions:
                </p>
                <div class="flex items-center space-x-2">
                    <!-- Placeholder for permissions/scopes -->
                    <!-- If checkbox component exists use it, otherwise simple input or stylized div -->
                    <div
                        class="space-y-2 border p-4 rounded-md w-full bg-white"
                    >
                        <div class="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="scope1"
                                checked
                                disabled
                                class="accent-primary"
                            />
                            <Label for="scope1">Read your profile</Label>
                        </div>
                        <div class="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="scope2"
                                checked
                                disabled
                                class="accent-primary"
                            />
                            <Label for="scope2">Access your email</Label>
                        </div>
                    </div>
                </div>
            </div>
        </CardContent>
        <CardFooter class="flex justify-between">
            <Button variant="ghost" onclick={handleDeny} disabled={isLoading}
                >Deny</Button
            >
            <Button onclick={handleAllow} disabled={isLoading}>
                {isLoading ? "Authorizing..." : "Allow Access"}
            </Button>
        </CardFooter>
    </Card>
</div>
