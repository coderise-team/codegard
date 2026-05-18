export default function RegistrationForm() {
  return (
    <form className="login-form" onSubmit={(e) => e.preventDefault()}>
      <h2>Create your account</h2>


      <div className="user-name">
        <label htmlFor="username">Username</label>
        <input
        id="username"
        name="username"
        type="Text"
        placeholder="Example_user"
        required
        />
      </div>

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
        Registrate
      </button>


    </form>
  )
}
