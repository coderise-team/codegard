export default function LoginForm() {
  return (
    <form className="login-form" onSubmit={(e) => e.preventDefault()}>
      <h2>Sign in to your account</h2>

      <div className="form-group">
        <label htmlFor="email">Email address</label>
        <input
          id="email"
          name="email"
          type="email"
          placeholder="you@example.com"
          required
        />
      </div>

      <div className="form-group">
        <div className="form-header">
          <label htmlFor="password">Password</label>
          <a href="#forgot">Forgot password?</a>
        </div>
        <input
          id="password"
          name="password"
          type="password"
          placeholder="••••••••"
          required
        />
      </div>

      <button type="submit" className="submit-btn">
        Sign in
      </button>


    </form>
  )
}
